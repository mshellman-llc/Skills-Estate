"""Assemble an isolated skill with explicit executable dependencies.

This is an assembly primitive, not a release decision. Callers must validate and
exercise the assembled result before installation or publication.
"""
from pathlib import Path
import json
import os
import re
import shutil

IGNORED = {".git", ".DS_Store", "__pycache__", ".venv", "node_modules", "_runtime"}
# A network share (SMB) leaves .smbdelete<id> placeholders for files deleted while open.
IGNORED_PREFIXES = (".smbdelete",)
UPDATER_MODULES = ('estate', 'updater', 'releases', 'committed_source', 'portable', 'catalog', 'marketplace_guard')

IDENTITY = {"SKILL.md", "skill.yaml", "skill.json", "agent.yaml", "agent.json", "AGENTS.md"}

PACKAGE_STANDARDS = ('\n## Shared standards\n\n'
    'Apply the [shared workflow](references/estate/workflow.md) and '
    '[writing standard](references/estate/writing.md).\n')


def runtime_closure(root, name, extra=()):
    root = Path(root)
    graph_path = root / 'config/runtime-dependencies.json'
    common_path = root / 'config/required-runtimes.json'
    graph = json.loads(graph_path.read_text()) if graph_path.exists() else {}
    common = json.loads(common_path.read_text()) if common_path.exists() else []
    if not isinstance(graph, dict) or not isinstance(common, list):
        raise ValueError('Runtime configuration must contain a graph object and required-runtime list')
    known = {p.name for p in (root / 'skills').iterdir() if (p / 'SKILL.md').is_file()}
    done, active, result = set(), set(), set()

    def visit(current):
        if not isinstance(current, str) or current not in known:
            raise ValueError(f'missing runtime dependency: {current}')
        if current in active:
            raise ValueError(f'Runtime dependency cycle at {current}')
        if current in done:
            return
        active.add(current)
        deps = graph.get(current, [])
        if not isinstance(deps, list):
            raise ValueError(f'Runtime dependencies for {current} must be a list')
        for dep in deps:
            visit(dep)
            result.add(dep)
        active.remove(current)
        done.add(current)

    visit(name)
    for dep in [*extra, *common]:
        if dep != name:
            visit(dep)
            result.add(dep)
    return sorted(result)


def source_files(directory):
    for parent, dirs, files in os.walk(directory, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in IGNORED)
        for name in dirs:
            if (Path(parent) / name).is_symlink():
                raise ValueError(f"Source directory symlink is not portable: {Path(parent) / name}")
        for name in sorted(files):
            file = Path(parent) / name
            if name in IGNORED or name.endswith(".pyc") or name.startswith(IGNORED_PREFIXES):
                continue
            if file.is_symlink():
                raise ValueError(f"Source symlink is not portable: {file}")
            yield file


def assemble(root, name, destination, dependencies, *, entrypoint_name='SKILL.md'):
    root, destination = Path(root).resolve(), Path(destination)
    if entrypoint_name not in {'SKILL.md', 'WORKFLOW.md'}:
        raise ValueError('Unsupported package entrypoint filename')
    if destination.exists():
        raise ValueError(f"Refusing to replace an existing package: {destination}")
    if name in dependencies or len(dependencies) != len(set(dependencies)):
        raise ValueError("Runtime dependencies must be unique and cannot include the entrypoint")
    dependencies = runtime_closure(root, name, dependencies)
    writing_required = (root / 'config/required-runtimes.json').exists()
    if writing_required:
        for policy in ('writing.md', 'workflow.md'):
            if not (root / 'policies' / policy).is_file():
                raise ValueError('Missing required shared policy: ' + policy)
    selected = [name, *dependencies]
    for skill in selected:
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", skill):
            raise ValueError(f"Invalid skill name: {skill}")
        if not (root / "skills" / skill / "SKILL.md").is_file():
            raise ValueError(f"Missing skill dependency: {skill}")

    mapping = {}
    for skill in selected:
        source = root / "skills" / skill
        prefix = Path() if skill == name else Path("_runtime") / skill
        for file in source_files(source):
            relative = file.relative_to(source)
            if skill == 'maintain-skills-estate' and relative.parts[:2] == ('scripts', 'estate_tools'):
                raise ValueError('scripts/estate_tools is generated, not authoring source')
            if relative.parts[:2] == ("references", "estate"):
                raise ValueError(f"references/estate is generated, not authoring source: {file}")
            if skill != name and len(relative.parts) == 1 and file.name in IDENTITY:
                if file.name == "SKILL.md":
                    # Preserve the complete workflow as a reference, with one
                    # discoverable SKILL.md at the package's top level.
                    mapping[file] = prefix / "WORKFLOW.md"
                continue
            mapping[file] = prefix / (entrypoint_name if skill == name and relative == Path('SKILL.md') else relative)
    # Ship the same reviewed implementation inside the maintenance package. Its
    # release link selects both workflows and updater code, including on rollback.
    if 'maintain-skills-estate' in selected:
        prefix = Path() if name == 'maintain-skills-estate' else Path('_runtime/maintain-skills-estate')
        for module in UPDATER_MODULES:
            source = root / 'tools' / (module + '.py')
            if not source.is_file() or source.is_symlink():
                raise ValueError('Missing portable updater module: ' + module)
            relative = prefix / 'scripts/estate_tools' / source.name
            if relative in mapping.values():
                raise ValueError('scripts/estate_tools is generated, not authoring source')
            mapping[source] = relative
    shared = root / "skills" / "_shared"
    if shared.exists():
        pending = []
        for file in list(mapping):
            # Selftests create synthetic paths, including intentionally missing
            # references. Keep their files in the package without treating those
            # fixture strings as runtime dependencies.
            if file.suffix in {".md", ".py", ".js", ".sh"} and not file.name.endswith("_selftest.py"):
                pending.extend(re.findall(r"_shared/([A-Za-z0-9_.-]+\.md)", file.read_text()))
        seen = set()
        while pending:
            name_of_shared_file = pending.pop()
            if name_of_shared_file in seen:
                continue
            seen.add(name_of_shared_file)
            file = shared / name_of_shared_file
            if not file.is_file():
                raise ValueError(f"Missing shared reference: {file}")
            mapping[file] = Path("_shared") / file.name
            for reference in re.findall(r"\]\(([^()\s]+)\)", file.read_text()):
                candidate = (file.parent / reference.split("#")[0]).resolve()
                if candidate.parent == shared and candidate.suffix == ".md":
                    pending.append(candidate.name)

    destination.mkdir(parents=True)
    try:
        for source, relative in mapping.items():
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.suffix == ".md":
                text = source.read_text()
                if writing_required and source == root / 'skills' / name / 'SKILL.md':
                    text = text.rstrip() + '\n' + PACKAGE_STANDARDS
                if source.name == 'SKILL.md' and relative.name == 'WORKFLOW.md':
                    header = re.match(r'\A---\n.*?\n---(?:\n|$)', text, re.S)
                    at = header.end() if header else 0
                    instruction = ('\nRun this module\'s relative commands from the directory containing '
                                   'this WORKFLOW.md. Resolve that directory to an absolute path first. '
                                   'A command that explicitly names another working directory keeps '
                                   'that requirement. This file is a supporting workflow, not another '
                                   'installed skill entrypoint.\n\n')
                    text = text[:at] + instruction + text[at:]

                def link(match):
                    href = match.group(1)
                    if href.startswith(("http:", "https:", "#", "/", "mailto:", "app:", "codex:")):
                        return match.group(0)
                    pathname, marker, fragment = href.partition("#")
                    resolved = (source.parent / pathname).resolve()
                    if resolved in mapping:
                        target_relative = os.path.relpath(destination / mapping[resolved], target.parent)
                        return "](" + target_relative + (marker + fragment if marker else "") + ")"
                    return match.group(0)

                text = re.sub(r"\]\(([^()\s]+)\)", link, text)
                # Shell snippets in entrypoints run from the package root.
                if source == root / "skills" / name / "SKILL.md":
                    for dep in dependencies:
                        text = text.replace(f"../{dep}/scripts/", f"_runtime/{dep}/scripts/")
                        text = text.replace(f"../{dep}/house.json", f"_runtime/{dep}/house.json")
                target.write_text(text)
                shutil.copymode(source, target)
            else:
                shutil.copy2(source, target)
        for skill in selected:
            package_root = destination if skill == name else destination / "_runtime" / skill
            policies = package_root / "references" / "estate"
            policies.mkdir(parents=True, exist_ok=True)
            for file in (root / "policies").glob("*.md"):
                shutil.copy2(file, policies / file.name)
        return {str(source.relative_to(root)): str(relative) for source, relative in mapping.items()}
    except BaseException:
        shutil.rmtree(destination)
        raise
