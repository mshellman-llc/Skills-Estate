#!/usr/bin/env python3
"""Install the writing check, hook and gate command on this computer.

    install_local.py [--git-hooks] [--services] [--dry]

Copies check.py, extract_review_text.py, hook.py, writing_system.py and
check_selection.py to ~/.agents/writing/bin with a manifest of their sha256, so
the hooks keep working whichever branch the repository has checked out. Writes
gate.json there when none exists, and the gate command for Claude Code
(~/.claude/commands/gate.md) and Codex (~/.codex/prompts/gate.md). When the
publish-content skill sits beside this one, its evidence_scan.py is copied too,
for the gate's check on client and public pieces.

--git-hooks  installs a hook folder whose every hook runs the repository's own hook
             first, then checks commit messages, and sets git's global
             core.hooksPath to it. Refuses when a global core.hooksPath is already set.
--services   builds the "Check writing" Services menu action in ~/Library/Services.

Hook settings for Claude Code and Codex are not edited here.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
HOME = Path.home()
BIN = HOME / '.agents' / 'writing' / 'bin'
FILES = ['check.py', 'extract_review_text.py', 'hook.py', 'writing_system.py', 'check_selection.py']
EVIDENCE_SCAN = SKILL.parent / 'publish-content' / 'scripts' / 'evidence_scan.py'
HOOK_NAMES = ['applypatch-msg', 'pre-applypatch', 'post-applypatch', 'pre-commit', 'pre-merge-commit',
              'prepare-commit-msg', 'commit-msg', 'post-commit', 'pre-rebase', 'post-checkout', 'post-merge',
              'pre-push', 'post-rewrite', 'pre-auto-gc']
DISPATCH = r'''#!/bin/sh
# Installed by the writing skill. Runs the repository's own hook of the same name, then checks commit messages.
name=$(basename "$0")
gitdir=$(git rev-parse --git-common-dir 2>/dev/null) || exit 0
own="$gitdir/hooks/$name"
if [ -x "$own" ]; then
  "$own" "$@" || exit $?
fi
if [ "$name" = "commit-msg" ] && [ -z "$WRITING_SKIP_COMMIT_CHECK" ]; then
  out=$(/usr/bin/env python3 "$HOME/.agents/writing/bin/check.py" --file "$1" --register commit --json 2>/dev/null)
  status=$(printf '%s' "$out" | /usr/bin/env python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("status",""))
except Exception: print("")')
  if [ "$status" = "fail" ]; then
    printf '%s' "$out" | /usr/bin/env python3 -c 'import json,sys
d=json.load(sys.stdin)
print("The commit message breaks the writing rules. Rewrite these lines:")
for h in d.get("findings", [])[:10]: print("  -", h.get("text"), "(" + str(h.get("rule")) + "):", h.get("fix", ""))'
    exit 1
  fi
fi
exit 0
'''


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def commit():
    out = subprocess.run(['git', '-C', str(SKILL), 'rev-parse', 'HEAD'], capture_output=True, text=True)
    return out.stdout.strip()


def install_bin(dry):
    BIN.mkdir(parents=True, exist_ok=True)
    manifest = {'source': str(HERE), 'commit': commit(), 'files': {}}
    for name in FILES:
        src = HERE / name
        if not dry:
            shutil.copy2(src, BIN / name)
        manifest['files'][name] = sha(src)
    if EVIDENCE_SCAN.is_file():
        if not dry:
            shutil.copy2(EVIDENCE_SCAN, BIN / EVIDENCE_SCAN.name)
        manifest['files'][EVIDENCE_SCAN.name] = sha(EVIDENCE_SCAN)
    if not dry:
        (BIN / 'MANIFEST.json').write_text(json.dumps(manifest, indent=1) + '\n')
        gate = BIN.parent / 'gate.json'
        if not gate.exists():
            sys.path.insert(0, str(HERE))
            import hook
            gate.write_text(json.dumps(hook.DEFAULT_GATE, indent=1) + '\n')
    return manifest


def install_commands(dry):
    text = (SKILL / 'assets' / 'gate-command.md').read_text(encoding='utf-8')
    targets = [HOME / '.claude' / 'commands' / 'gate.md', HOME / '.codex' / 'prompts' / 'gate.md']
    for target in targets:
        if not dry:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding='utf-8')
    return [str(t) for t in targets]


def install_git_hooks(dry):
    current = subprocess.run(['git', 'config', '--global', '--get', 'core.hooksPath'], capture_output=True,
                             text=True).stdout.strip()
    folder = BIN.parent / 'git-hooks'
    if current and Path(current).expanduser() != folder:
        sys.exit(f'global core.hooksPath is already {current}; not replacing it')
    if not dry:
        folder.mkdir(parents=True, exist_ok=True)
        dispatch = folder / 'dispatch'
        dispatch.write_text(DISPATCH)
        dispatch.chmod(0o755)
        for name in HOOK_NAMES:
            link = folder / name
            if link.exists() or link.is_symlink():
                link.unlink()
            link.symlink_to('dispatch')
        subprocess.run(['git', 'config', '--global', 'core.hooksPath', str(folder)], check=True)
    return str(folder)


def workflow_plist(command):
    ids = [str(uuid.uuid4()).upper() for _ in range(3)]
    esc = command.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>AMApplicationBuild</key><string>523</string>
	<key>AMApplicationVersion</key><string>2.10</string>
	<key>AMDocumentVersion</key><string>2</string>
	<key>actions</key>
	<array>
		<dict>
			<key>action</key>
			<dict>
				<key>AMAccepts</key>
				<dict><key>Container</key><string>List</string><key>Optional</key><true/>
				<key>Types</key><array><string>com.apple.cocoa.string</string></array></dict>
				<key>AMActionVersion</key><string>2.0.3</string>
				<key>AMApplication</key><array><string>Automator</string></array>
				<key>AMParameterProperties</key>
				<dict><key>COMMAND_STRING</key><dict/><key>CheckedForUserDefaultShell</key><dict/>
				<key>inputMethod</key><dict/><key>shell</key><dict/><key>source</key><dict/></dict>
				<key>AMProvides</key>
				<dict><key>Container</key><string>List</string>
				<key>Types</key><array><string>com.apple.cocoa.string</string></array></dict>
				<key>ActionBundlePath</key><string>/System/Library/Automator/Run Shell Script.action</string>
				<key>ActionName</key><string>Run Shell Script</string>
				<key>ActionParameters</key>
				<dict><key>COMMAND_STRING</key><string>{esc}</string>
				<key>CheckedForUserDefaultShell</key><true/>
				<key>inputMethod</key><integer>0</integer>
				<key>shell</key><string>/bin/zsh</string>
				<key>source</key><string></string></dict>
				<key>BundleIdentifier</key><string>com.apple.RunShellScript</string>
				<key>CFBundleVersion</key><string>2.0.3</string>
				<key>CanShowSelectedItemsWhenRun</key><false/>
				<key>CanShowWhenRun</key><true/>
				<key>Category</key><array><string>AMCategoryUtilities</string></array>
				<key>Class Name</key><string>RunShellScriptAction</string>
				<key>InputUUID</key><string>{ids[0]}</string>
				<key>Keywords</key><array><string>Shell</string><string>Script</string></array>
				<key>OutputUUID</key><string>{ids[1]}</string>
				<key>UUID</key><string>{ids[2]}</string>
				<key>UnlocalizedApplications</key><array><string>Automator</string></array>
				<key>arguments</key><dict/>
				<key>isViewVisible</key><integer>1</integer>
				<key>location</key><string>309.5:253.0</string>
			</dict>
			<key>isViewVisible</key><integer>1</integer>
		</dict>
	</array>
	<key>connectors</key><dict/>
	<key>workflowMetaData</key>
	<dict>
		<key>serviceInputTypeIdentifier</key><string>com.apple.Automator.text</string>
		<key>serviceOutputTypeIdentifier</key><string>com.apple.Automator.nothing</string>
		<key>serviceProcessesInput</key><integer>0</integer>
		<key>workflowTypeIdentifier</key><string>com.apple.Automator.servicesMenu</string>
	</dict>
</dict>
</plist>
'''


INFO_PLIST = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>NSServices</key>
	<array>
		<dict>
			<key>NSMenuItem</key><dict><key>default</key><string>Check writing</string></dict>
			<key>NSMessage</key><string>runWorkflowAsService</string>
			<key>NSSendTypes</key><array><string>public.utf8-plain-text</string></array>
		</dict>
	</array>
</dict>
</plist>
'''


def install_services(dry):
    target = HOME / 'Library' / 'Services' / 'Check writing.workflow'
    if not dry:
        contents = target / 'Contents'
        contents.mkdir(parents=True, exist_ok=True)
        command = '/usr/bin/env python3 "$HOME/.agents/writing/bin/check_selection.py"'
        (contents / 'document.wflow').write_text(workflow_plist(command), encoding='utf-8')
        (contents / 'Info.plist').write_text(INFO_PLIST, encoding='utf-8')
        subprocess.run(['/System/Library/CoreServices/pbs', '-update'], capture_output=True)
    return str(target)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--git-hooks', action='store_true')
    ap.add_argument('--services', action='store_true')
    ap.add_argument('--dry', action='store_true')
    args = ap.parse_args(argv)
    report = {'bin': install_bin(args.dry), 'commands': install_commands(args.dry)}
    if args.git_hooks:
        report['git_hooks'] = install_git_hooks(args.dry)
    if args.services:
        report['services'] = install_services(args.dry)
    print(json.dumps(report, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
