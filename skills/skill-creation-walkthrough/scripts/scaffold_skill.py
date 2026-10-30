#!/usr/bin/env python3
"""Create a local draft from a supplied workflow and bundled intake templates."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE.parent / "templates/skill"
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
RUNTIMES = ("generic-agent-skills", "codex", "claude-code", "claude-ai", "cowork", "chatgpt")


def substitute(value, replacements):
    if isinstance(value, str):
        return replacements.get(value, value)
    if isinstance(value, list):
        return [substitute(v, replacements) for v in value]
    if isinstance(value, dict):
        return {k: substitute(v, replacements) for k, v in value.items()}
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name")
    parser.add_argument("--root", required=True, type=Path,
                        help="Existing project root; writes only skills/<name> beneath it")
    parser.add_argument("--display-name", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--workflow", required=True, type=Path,
                        help="Markdown body containing the actual task-specific procedure")
    parser.add_argument("--reference", action="append", default=[], type=Path)
    parser.add_argument("--runtime", action="append", required=True, choices=RUNTIMES)
    parser.add_argument("--tier", choices=("core", "situational", "maintainer"), default="situational")
    parser.add_argument("--knowledge-hub", choices=("required", "optional", "not-applicable"),
                        default="not-applicable")
    args = parser.parse_args()
    try:
        if not NAME.fullmatch(args.name) or len(args.name) > 64:
            raise ValueError("Name must be lowercase hyphen-case, at most 64 characters")
        for label in ("display_name", "description", "owner", "category"):
            text = getattr(args, label)
            if not text.strip() or any(ord(c) < 32 for c in text):
                raise ValueError(label + " must be one nonempty line without control characters")
        if len(args.description) > 1024:
            raise ValueError("Description exceeds 1024 characters")
        root = args.root.resolve(strict=True)
        if not root.is_dir():
            raise ValueError("--root must be an existing directory")
        parent = root / "skills"
        if parent.is_symlink():
            raise ValueError("The skills directory must not be a symlink")
        destination = parent / args.name
        if destination.exists() or destination.is_symlink():
            raise ValueError("Destination already exists; this command never overwrites a skill")
        workflow = args.workflow.read_text()
        if not workflow.strip() or workflow.lstrip().startswith("---"):
            raise ValueError("--workflow must contain a Markdown body without frontmatter")
        if re.search(r"\bTODO\b|replace-with-", workflow):
            raise ValueError("Complete the workflow placeholders before scaffolding")
        resources = {}
        for source in args.reference:
            if source.name in resources:
                raise ValueError("Reference filenames collide: " + source.name)
            try:
                resources[source.name] = source.read_bytes()
            except OSError as error:
                raise ValueError(f"Cannot read --reference {source}: {error.strerror}") from error
        # Only the original template placeholders are expanded. Supplied text is
        # never interpreted as a second template or as YAML syntax.
        replacements = {
            "replace-with-skill-name": args.name,
            "Replace With Display Name": args.display_name,
            "replace-with-description": args.description,
            "team-or-person": args.owner,
            "capability-area": args.category,
            "replace-with-runtimes": list(dict.fromkeys(args.runtime)),
            "replace-with-tier": args.tier,
            "replace-with-hub-requirement": args.knowledge_hub,
        }
        metadata = substitute(json.loads((TEMPLATES / "skill.yaml").read_text()), replacements)
        if args.knowledge_hub == "required":
            metadata["depends_on"] = ["knowledge-hub"]
        metadata["triggers"] = [args.description]
        template = (TEMPLATES / "skill-entry.md.tmpl").read_text()
        text_values = {
            "replace-with-skill-name": args.name,
            "replace-with-description": json.dumps(args.description, ensure_ascii=False),
            "Replace With Display Name": args.display_name,
            "replace-with-workflow": workflow.rstrip(),
        }
        pattern = re.compile("|".join(re.escape(k) for k in text_values))
        entry = pattern.sub(lambda m: text_values[m.group()], template)
        governance = (TEMPLATES / "governance.yaml").read_text()
        governance = re.sub("replace-with-skill-name|team-or-person",
                            lambda m: args.name if m.group() == "replace-with-skill-name"
                            else json.dumps(args.owner, ensure_ascii=False), governance)
        pending = {
            "SKILL.md": entry.encode(),
            "skill.yaml": (json.dumps(metadata, indent=2, ensure_ascii=False) + "\n").encode(),
            "fixtures/governance.yaml": governance.encode(),
            **{"references/" + name: content for name, content in resources.items()},
        }
        # Content and inputs are read before creating the destination.
        parent.mkdir(exist_ok=True)
        destination.mkdir()
        try:
            for name, content in pending.items():
                path = destination / name
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("xb") as output:
                    output.write(content)
            receipt = {
                "state": "draft", "created_at": datetime.now(timezone.utc).isoformat(),
                "destination": str(destination),
                "runtime_declarations": metadata["runtimes"],
                "runtime_verified": [],
                "workflow_sha256": hashlib.sha256(args.workflow.read_bytes()).hexdigest(),
                "files": {name: hashlib.sha256(content).hexdigest()
                          for name, content in pending.items()},
                "next": "Complete the intake and run the workflow on representative inputs; creation is not installation.",
            }
            (destination / "fixtures/scaffold-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
        except BaseException:
            shutil.rmtree(destination)
            raise
        print(json.dumps(receipt, indent=2))
        return 0
    except (OSError, ValueError, TypeError) as error:
        parser.exit(2, str(error) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
