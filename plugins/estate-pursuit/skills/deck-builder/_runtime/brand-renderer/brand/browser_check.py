"""Run a packaged Playwright check and retain every attempt."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def run_check(document, script, output=None):
    document, script = Path(document).resolve(), Path(script).resolve()
    base = Path(output) if output else document.parent / '.verification'
    base.mkdir(parents=True, exist_ok=True)
    attempt = Path(tempfile.mkdtemp(prefix=document.stem + '-', dir=base))
    report = {'document': str(document), 'checks': {}, 'failures': [], 'exitCode': 2}
    try:
        report['inputSha256'] = hashlib.sha256(document.read_bytes()).hexdigest()
        shutil.copy2(document, attempt / 'input.html')
        shutil.copy2(script, attempt / 'verify.mjs')
        node = os.environ.get('ESTATE_NODE') or shutil.which('node')
        if not node:
            raise ValueError('Node.js is missing; set ESTATE_NODE to its executable')
        roots = [Path(x) for x in os.environ.get('ESTATE_NODE_MODULES', '').split(os.pathsep) if x]
        roots += [Path(x) for x in os.environ.get('NODE_PATH', '').split(os.pathsep) if x]
        roots += [parent / 'node_modules' for parent in [Path.cwd(), *Path.cwd().parents]]
        entry = next((root / 'playwright' / name for root in roots
                      for name in ('index.mjs', 'index.js') if (root / 'playwright' / name).is_file()), None)
        if entry is None:
            raise ValueError('Playwright is missing; set ESTATE_NODE_MODULES to its node_modules directory')
        result = subprocess.run(
            [node, str(attempt / 'verify.mjs'), document.as_uri(), str(attempt)],
            env={**os.environ, 'PW_MODULE': entry.resolve().as_uri()},
            capture_output=True, text=True, timeout=180)
        (attempt / 'console.log').write_text(result.stdout + result.stderr)
        browser = json.loads(result.stdout)
        report.update(browser)
        report['exitCode'] = result.returncode or (2 if report['failures'] else 0)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        report['failures'].append(str(exc))
        report['exitCode'] = 2
        if not (attempt / 'console.log').exists():
            (attempt / 'console.log').write_text(str(exc) + '\n')
    (attempt / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    print('Saved browser attempt: ' + str(attempt))
    return report['exitCode']
