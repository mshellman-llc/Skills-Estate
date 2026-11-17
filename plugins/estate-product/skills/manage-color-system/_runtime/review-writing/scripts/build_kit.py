#!/usr/bin/env python3
"""Build host setup files from a checked standalone skill ZIP."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import zipfile

HERE = Path(__file__).resolve().parents[1]
HOSTS = {
    'codex': ('Codex', 'Use the reviewed local skill installation mechanism and the existing AGENTS.md route. Check the current Skills Estate installer before promotion. Use a separate temporary home for install tests.'),
    'claude-code': ('Claude Code', 'Use the reviewed local skill installation mechanism and the existing CLAUDE.md route. Preserve other installed skills. Use a separate owner-confirmed profile store; do not reuse other profiles automatically. Pass its explicit path as --store to every learning.py command.'),
    'claude-ai': ('Claude.ai or Claude Cowork', 'Use the native skill interface for review-writing.zip. Verify that it is enabled and loaded. Inspect persistent project files and file-editing tools before choosing a storage mode. An uploaded skill alone does not establish writable cross-session learning storage.'),
    'chatgpt': ('ChatGPT', 'Use the web instructions and companion files in a private Project. Use supported project instructions or custom instructions for the standing instruction. Inspect the connected file tools and test whether they can update a persistent profile.'),
    'gemini': ('Gemini', 'Use the web instructions and companion files in a private Gem or supported workspace. Inspect its actual file tools. Keep the owner profile private and test whether its saved version can be retrieved in a new conversation.'),
    'generic': ('this AI tool', 'Inspect the supported skill and persistent file mechanisms. Use the executable ZIP when possible, otherwise implement the web workflow with the supplied files. Do not infer unavailable capabilities from another host’s limitations.')
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(package, destination, owner, profile):
    destination = Path(destination)
    if destination.exists():
        raise ValueError('Choose a new kit directory; existing deliverables are preserved.')
    if not owner.strip() or len(owner) > 100 or '\n' in owner:
        raise ValueError('Supply the owner’s chosen name on one line.')
    import re
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', profile):
        raise ValueError('Supply a lowercase profile ID.')
    with tempfile.TemporaryDirectory(prefix='writing-setup-') as tmp:
        stage = Path(tmp)
        with zipfile.ZipFile(package) as z:
            if z.testzip() is not None:
                raise ValueError('The package ZIP failed its integrity check.')
            for name in ['scripts/learning.py', 'scripts/build_kit.py', 'references/learning.md', 'references/host-setup.md', 'assets/setup/setup-prompt.md', 'assets/setup/web-instructions.md', 'assets/setup/README.md']:
                if z.read('review-writing/' + name) != (HERE/name).read_bytes():
                    raise ValueError('The checked package differs from current source: ' + name)
            pinned = {name: z.read('review-writing/' + name).decode() for name in [
                'SKILL.md', 'assets/setup/README.md', 'assets/setup/web-instructions.md',
                'assets/setup/setup-prompt.md', 'references/learning.md', 'references/host-setup.md',
                *['references/' + name + '.md' for name in ['patterns', 'expanded-writing-review', 'context-rules', 'detailed-review', 'examples']]]}
            source = pinned['SKILL.md']
            if 'Capture and consolidate corrections' not in source:
                raise ValueError('The ZIP does not contain the learning revision.')
        shutil.copy2(package, stage/'review-writing.zip')
        assets = HERE/'assets/setup'
        (stage/'README.md').write_text(pinned['assets/setup/README.md'])
        (stage/'writing-integrity-web.md').write_text(pinned['assets/setup/web-instructions.md'])
        workflow = pinned['references/learning.md'].replace('[host setup](host-setup.md)', '[host setup](#host-setup-and-verification)')
        (stage/'learning-workflow.md').write_text(workflow+'\n\n'+pinned['references/host-setup.md'])
        library = []
        for name in ['patterns','expanded-writing-review','context-rules','detailed-review','examples']:
            fragment = pinned['references/' + name + '.md']
            targets = {'patterns.md': '#sentence-patterns', 'expanded-writing-review.md': '#paragraphs-claims-and-response-habits', 'context-rules.md': '#requirements-for-particular-kinds-of-writing', 'examples.md': '#editing-examples', 'learning.md': 'learning-workflow.md', '../../writing-diagnostics/SKILL.md': 'review-writing.zip', '../_runtime/writing-diagnostics/WORKFLOW.md': 'review-writing.zip'}
            for old, new in targets.items():
                fragment = fragment.replace('](' + old + ')', '](' + new + ')')
            library.append(fragment)
        (stage/'review-library.md').write_text('# Writing review library\n\nRetrieve the section needed for the current problem. The web entrypoint supplies the required checks.\n\n'+'\n\n'.join(library))
        payload={'version':1,'owner':owner,'profile':profile,'created':'initialize-on-setup','rules':[],'events':[]}
        (stage/'profile-starter.json').write_text(json.dumps({'payload':payload},indent=2)+'\n')
        (stage/'profile-starter.md').write_text(f'# Writing profile for {owner}\n\nProfile ID: {profile}. No learned rules are active yet. Initialize the private correction store or manual files during setup.\n')
        prompt=pinned['assets/setup/setup-prompt.md']
        for host,(name,route) in HOSTS.items():
            content=prompt.replace('{{HOST_NAME}}',name).replace('{{OWNER}}',owner).replace('{{PROFILE}}',profile).replace('{{HOST_ID}}',host).replace('{{HOST_ROUTE}}',route)
            (stage/f'setup-{host}.md').write_text(content)
        (stage/'standing-instruction.txt').write_text('Use review-writing for authored text. Read the current compact owner profile authorized for the current task at task start. Keep profile storage separate from other profiles, even for the same owner. Pass an explicit authorized path as --store to every learning.py command. When learning is enabled, capture actual writing corrections and substantive AI repairs as they happen. Consolidate supported rules and checkpoint before finishing a task. Keep private history separate from the active profile, which must stay within 12 rules and 350 words. Load detailed references only for the current problem. Verify saved changes; if persistence is unavailable, return the changed profile and transfer files with the exact replacement step.\n')
        for file in stage.glob('*.md'):
            for href in re.findall(r'\]\(([^\s)]+)(?:\s+[^)]*)?\)', file.read_text()):
                if ':' not in href and not href.startswith(('#', '/')) and not (file.parent / href.split('#')[0]).exists():
                    raise ValueError('Unresolved setup file reference: ' + href)
        manifest={'format':1,'owner':owner,'profile':profile,'skill_zip_sha256':sha(Path(package)),
                  'files':{p.name:sha(p) for p in sorted(stage.iterdir())}}
        (stage/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copytree(stage,destination)
    return manifest


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--owner',required=True);ap.add_argument('--profile',required=True)
    args=ap.parse_args()
    try:
        result=build(args.package,args.output,args.owner,args.profile)
        print(json.dumps({'directory':str(args.output.resolve()),'files':len(result['files']),'skill_zip_sha256':result['skill_zip_sha256']},indent=2));return 0
    except (ValueError,OSError,KeyError,zipfile.BadZipFile) as exc:
        print(str(exc));return 2


if __name__=='__main__':
    raise SystemExit(main())
