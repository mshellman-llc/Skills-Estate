---
skill: skill-estate-sync
title: Diagnose a stale build and a skill in the wrong plugin
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 9c825654bbc5796ce092366a36a8d9d67a5928156d7addcf3c194c2ef495011d
---

## Request

After pulling main, our status check says the build is stale and contract-redline is showing up in the finance plugin instead of legal. I've pasted the status output and the two config excerpts; work out why and tell me what to do next, but don't install or publish anything.

## Inputs

**Dry run.** This skill normally works on live systems or its owner's own setup. Here the system state is invented in the inputs below, and nothing was changed anywhere. Run of the built `skill-estate-sync` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### config-excerpts.md

#### config/skill-catalog.json (excerpt)

```json
{
  "tasks": {
    "contract-redline":  { "domain": "legal",   "modes": ["redline", "clause-compare"] },
    "invoice-matcher":   { "domain": "finance", "modes": ["match", "variance"] },
    "board-pack-builder":{ "domain": "finance", "modes": ["assemble"] },
    "clause-library":    { "domain": "legal",   "modes": ["lookup"] },
    "matter-intake":     { "domain": "legal",   "modes": ["intake"] }
  }
}
```

#### config/plugin-bundles.json (excerpt)

```json
{
  "version": "1.14.0",
  "plugins": {
    "estate-finance": { "tasks": ["invoice-matcher", "contract-redline", "board-pack-builder"] },
    "estate-legal":   { "tasks": ["clause-library", "matter-intake"] }
  }
}
```

#### git log -3 --oneline -- config/plugin-bundles.json config/skill-catalog.json

```
4be91c2 Merge branch 'legal-domain' (catalog: contract-redline domain finance -> legal)
9e0d7a4 Add matter-intake task
c3b18f0 Move contract-redline into estate-finance bundle for Q3 vendor review
```

#### config/plugin-version-history.json (latest entry)

```json
{ "version": "1.14.0", "fingerprint": "e90b…c4", "note": "Add matter-intake task" }
```

#### status-output.txt

$ python3 tools/estate.py status      (checkout: ~/src/Lindqvist-Estate, branch main @ 4be91c2)

source hash (current):   a7f3c10e92
build/ source hash:      5d21be8847      STALE
dist/ ZIPs hash:         5d21be8847      STALE (matches build, not source)

installed release:       rel-2026-10-21-1   (source 5d21be8847)
  ~/.claude/skills/contract-redline    linked-current -> rel-2026-10-21-1
  ~/.claude/skills/invoice-matcher     linked-current -> rel-2026-10-21-1
  ~/.claude/skills/board-pack-builder  pinned-older   -> rel-2026-09-02-1
  ~/.agents/skills/contract-redline    linked-current -> rel-2026-10-21-1
  ~/.codex/skills/invoice-matcher      legacy-mutable (divergent file: notes.md)

plugin candidates (plugins/):
  estate-finance      1.14.0   contains: invoice-matcher, contract-redline, board-pack-builder
  estate-legal        1.14.0   contains: clause-library, matter-intake

account uploads (publish-ledger): claude-account/invoice-matcher  verified_live: false

overall: FAIL (build stale; 1 pinned-older; 1 legacy-mutable)

## Output

There are two separate problems. Neither needs an install to fix, and I haven't installed or published anything. I worked only from the pasted status output and config excerpts and ran no commands, so everything below comes from those files.

#### 1. Why the build is stale

`status` compares three hashes:

| Item | Hash |
| --- | --- |
| Current source (`main` @ `4be91c2`) | `a7f3c10e92` |
| `build/` | `5d21be8847` |
| `dist/` ZIPs | `5d21be8847` |
| Installed `rel-2026-10-21-1` | `5d21be8847` |

The merge of `legal-domain` changed source after the last build. The build and ZIPs are consistent with each other but were made from the older source. The installed release was also built from that older source. So the installed `contract-redline` is linked correctly and still carries the old domain.

Rebuilding refreshes the candidates only. It does not change what is installed.

#### 2. Why contract-redline is in the finance plugin

Two config files answer different questions:

- `config/skill-catalog.json` says what each task is. The merge `4be91c2` changed `contract-redline` from `finance` to `legal` there.
- `config/plugin-bundles.json` decides which plugin ships each task. It still lists `contract-redline` under `estate-finance` and not under `estate-legal`.

Commit `c3b18f0` ("Move contract-redline into estate-finance bundle for Q3 vendor review") put it in the finance bundle on purpose. The merge touched the catalog but not the bundle file, so the bundle assignment is still the Q3 one. The `plugins/` candidates (`estate-finance` has three tasks, `estate-legal` has two) match the bundle file exactly, so the generator is working as designed.

**Assumption:** the Q3 vendor review is over, so the task should now live in legal only. If finance still needs it, keep it in both bundles. The skill allows a task in more than one plugin only if the bundle file says so. I would not assume that.

#### What to do next

Run these from the checkout root, in order:

1. Edit `config/plugin-bundles.json`. Remove `contract-redline` from `estate-finance` and add it to `estate-legal`.
2. Run `python3 tools/estate.py validate`. It catches broken links and missing runtime dependencies in `config/runtime-dependencies.json`.
3. Run the tests for `contract-redline`, using representative inputs, and save the actual outputs. Moving a task between plugins changes its routing, so also check that legal requests reach it and that finance requests such as invoice matching still go to `invoice-matcher`. Then run `python3 tools/run_tests.py --report .local/test-results.json`. A successful build only shows that packaging works, not that the skill can do its job.
4. Raise `version` in `config/plugin-bundles.json` from `1.14.0`. The history entry for `1.14.0` is bound to the old content ("Add matter-intake task"), and reusing a version for changed content fails. Then record the change:
   ```sh
   python3 tools/plugin_version.py --record 'Move contract-redline from estate-finance to estate-legal after the Q3 vendor review.'
   python3 tools/plugins.py --candidate
   ```
5. Run `python3 tools/estate.py sync`. This runs build and bundle only. Check that the new source hash appears in `build/` and `dist/`.
6. Open the generated `plugins/estate-legal` and `plugins/estate-finance` and the host manifests. Confirm that `contract-redline` appears in legal only, with its transitive dependencies.

Do not edit anything under `plugins/`, `build/`, `dist/` or the installed copies. Those are generated.

#### Other items in the status output

- **`board-pack-builder` is `pinned-older`** (`rel-2026-09-02-1`). It still works and needs no action unless you want it current. Promote it on its own later with `install --skill board-pack-builder --expected-source <reviewed hash>`.
- **`~/.codex/skills/invoice-matcher` is `legacy-mutable`** and has a divergent `notes.md`. Open that file first. If it holds work you want, move it into the source skill. Only then consider a scoped `adopt --skill invoice-matcher --expected-source <reviewed hash>`, which backs up the original and writes a restore receipt. Don't discard it to get a green status.
- **The publish ledger** lists `claude-account/invoice-matcher` with `verified_live: false`. That row records an upload hash only. It is not evidence that the skill ran in that account.

#### Before anything is installed

After steps 1–6 and an independent review, install only with the reviewed source hash. Use `install --expected-source <hash>`, or `--skill contract-redline` to promote that one package and leave the other links alone. Afterwards, open a fresh Claude Code session and run a real contract-redline task there. A Codex run does not count as Claude Code evidence. Publishing to the marketplace is a separate step that needs your authorization.

#### Status of this work

- Diagnosis: done, from the pasted files.
- Source change, tests, version bump, rebuild: not done; the steps are above.
- Installed releases: unchanged.
- Published or uploaded: nothing.
