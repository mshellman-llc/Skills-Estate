# Test execution

Run `python3 tools/run_tests.py --report .local/test-results.json` for the local default. It runs parsing, package assembly, document generation, validation, request-handler, and synthetic browser-policy checks. It never selects real browser or loopback tests. Its report lists every deferred test and distinguishes `passed_with_deferred` from a complete pass. Any other skipped test reports `incomplete` and returns a failure status.

Install the pinned Python and Node dependencies before running the suite. Node-based DOCX/PPTX generation and fake browser-policy tests remain part of default coverage; missing required tools are errors. `ESTATE_NODE` selects Node, while `ESTATE_NODE_MODULES` and `NODE_PATH` locate its dependencies.

Use `--integration browser` only in an environment approved for browser execution. It checks runtime files without launching, then runs the preserved DOM, rendering and PDF assertions. Missing dependencies or an actual render failure fail the run. Installed macOS Google Chrome remains prohibited by the shared launch policy. No test command installs a browser or retries a failed launch with elevated permissions.

Use `--integration loopback` to exercise the real local HTTP transport. The default suite separately calls the production request handlers to check host, origin, nonce, body, route and locking rules without binding a socket.

The map tests build an isolated snapshot from current source. Use `--integration generated-map` after rebuilding the published artifact to check its freshness against source. A stale checked-in map must not make the builder's unit fixture stale too.

CI installs the pinned browser runtime, rebuilds the map from its intended Git baseline, and runs `--all-integrations`. `--list` shows test classifications without probing runtimes or running tests. Plain unittest discovery also defers unselected integration methods; it does not provide the runner's consolidated report.
