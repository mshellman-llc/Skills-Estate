#!/usr/bin/env python3
"""Run a Python self-test while retaining its temporary files and console log.

Each invocation creates a distinct attempt directory. Temporary directories are
copied before their normal cleanup, preserving test semantics and failed output.
Use only with trusted estate tests and synthetic fixtures.
"""
import argparse
import contextlib
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import sys
import tempfile
import traceback


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("test", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    test = args.test.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    attempt = Path(tempfile.mkdtemp(prefix=test.stem + "-", dir=args.output)).resolve()
    original = tempfile.TemporaryDirectory
    retained = []
    errors = []

    class PreservedDirectory(original):
        def cleanup(self):
            source = Path(self.name)
            if source.exists():
                destination = attempt / ("temporary-{:03d}".format(len(retained) + 1))
                try:
                    shutil.copytree(source, destination, symlinks=True)
                    retained.append(str(destination.relative_to(attempt)))
                except Exception as exc:
                    errors.append(str(exc))
                    # Keep the original if its evidence could not be copied.
                    self._finalizer.detach()
                    retained.append(str(source))
                    return
            super().cleanup()

    code = 0
    tempfile.TemporaryDirectory = PreservedDirectory
    try:
        with (attempt / "console.log").open("w") as log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            try:
                sys.argv = [str(test)]
                sys.path.insert(0, str(test.parent))
                runpy.run_path(str(test), run_name="__main__")
            except SystemExit as exc:
                code = int(exc.code) if isinstance(exc.code, int) else (1 if exc.code else 0)
            except BaseException:
                traceback.print_exc()
                code = 1
    finally:
        tempfile.TemporaryDirectory = original
    result = {"test": str(test), "testSha256": hashlib.sha256(test.read_bytes()).hexdigest(),
              "exitCode": code, "retainedDirectories": retained, "retentionErrors": errors}
    (attempt / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"attempt": str(attempt), **result}, indent=2))
    return code or (1 if errors else 0)


if __name__ == "__main__":
    raise SystemExit(main())
