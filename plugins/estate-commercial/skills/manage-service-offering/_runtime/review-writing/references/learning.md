# Learning from corrections

Keep the active writing profile short. Save the actual misses and replacements in a separate private store. Read this workflow when enrolling an installation, capturing a correction, consolidating rules or transferring a profile.

## Enroll the installation

An installation has a storage location and an explicit owner. The skill's folder does not identify its owner. Tools may share a private profile only when its owner authorized that profile for their current tasks. Keep profiles separate when their authorized contexts differ. Use host or project scope for a preference that applies only there. Keep another person's profile separate.

Run the helper from the installed skill's absolute folder. Python 3.9 or later is sufficient; it uses the standard library. Substitute the available Python command if the host uses `python` or `py -3` instead of `python3`. The helper requires an explicit `--store PATH`; it does not read a profile from an environment variable or default directory. Set `PROFILE_STORE` to a confirmed private context location separate from profiles authorized for other contexts, even for the same owner. Keep the store outside repositories and skill packages. Without a confirmed location, use core writing review without learned preferences.

```sh
python3 scripts/learning.py --store "$PROFILE_STORE" init --owner "OWNER" --profile-id PROFILE --host HOST --durability persistent --enable-learning
python3 scripts/learning.py --store "$PROFILE_STORE" status
python3 scripts/learning.py --store "$PROFILE_STORE" context --host HOST --tags general,FORMAT --markdown
```

Replace the uppercase values. Use a chosen lowercase profile ID such as `writer` and a host ID such as `codex`, `claude-code`, `claude-ai`, `chatgpt` or `gemini`. The owner is a person's chosen name. A project ID must be explicit; do not derive ownership or a company voice from a directory.

Enable learning only when the installing owner requests it. Keep the owner’s request and its source reference in the private setup record. That request authorizes routine correction capture and reviewed profile maintenance for this owner, including substantive AI repairs; the owner need not repeat “remember this” for each correction after enrollment. An AI repair remains evidence for review, not a personal preference. This authorization does not permit reading other chats, uploading private examples or changing another person’s profile.

Choose `persistent` only after reopening the store in a new process and reading a saved record. Use `session` for temporary compute storage and `manual` when files must be carried into the next chat. An installation record is a claim about the selected storage; the host setup test must verify it. Use available storage tools before concluding that persistence is unavailable.

## Capture a miss while the evidence is available

Fix the affected writing, then record the smallest before and after excerpts needed to explain the repair. Capture the reason, source reference, host, task session and applicable project. Redact private names and other details the writing lesson does not need. Never store credentials or a whole transcript as an example.

Use a JSON file to avoid shell quoting mistakes:

```json
{
  "session": "task-identifier",
  "pattern": "direct-claim",
  "host": "codex",
  "project": "",
  "kind": "user-correction",
  "before": "The result? Saved.",
  "after": "The file is saved.",
  "reason": "State the outcome directly.",
  "source_ref": "Current conversation, correction 1",
  "tags": ["general"]
}
```

```sh
python3 scripts/learning.py --store "$PROFILE_STORE" capture correction.json
python3 scripts/learning.py --store "$PROFILE_STORE" pending
python3 scripts/learning.py --store "$PROFILE_STORE" examples --pattern direct-claim --limit 2
```

Use `user-correction` for an actual user correction and `ai-repair` for the AI's own repair. Keep a proposed replacement provisional until the text has actually been revised. A self-edit does not establish the user's voice. Repeated capture of the same event in the same host and session returns the existing ID.

The source reference must identify evidence available in this session or an explicitly supplied file. Import material from another AI only when the owner supplies it or authorizes access. A tool must not search unrelated conversations to build a writing profile.

## Review a candidate before activating it

Use one pattern ID for the same failure. Check an existing rule before adding another. Review whether the proposed instruction repairs the miss, preserves the required meaning and leaves a valid example alone. Use examples where facts, conditions or the author's voice could be lost. Record the actual input, output and assessment for each case.

`promote` validates the record and budget. It does not judge prose or independently verify the reviewer's assessment. The reviewing AI must read the examples and compare the results. For a consequential change, use an independent review when available within the authorized work.

A proposal has these fields. Leave `exception` empty when no exception is justified; do not invent one to fill the record:

```json
{
  "pattern": "direct-claim",
  "scope": "general",
  "instruction": "State the outcome directly.",
  "exception": "Keep a question when the reader needs it answered.",
  "tags": ["general"],
  "evidence": ["EVENT_ID_FROM_CAPTURE"],
  "review": {
    "basis": "user-correction",
    "meaning": "The repair preserves the saved-file result.",
    "scope": "The instruction applies to routine replies.",
    "valid_example": "A question that identifies a missing decision is retained.",
    "cases": [
      {"kind": "repair", "input": "The result? Saved.", "output": "The file is saved.", "assessment": "States the result directly.", "result": "pass"},
      {"kind": "keep", "input": "Which account should receive the file?", "output": "Which account should receive the file?", "assessment": "Keeps the necessary decision question.", "result": "pass"}
    ]
  }
}
```

```sh
python3 scripts/learning.py --store "$PROFILE_STORE" promote proposal.json
```

Use `writing-standard` as the basis for an AI repair and include `standard_ref` in the review. Identify the existing writing rule that supports the change. Personal voice needs user evidence. A profile cannot weaken facts, privacy, legal meaning or authorization requirements.

For a host rule, set `scope` to `host` and `scope_id` to its host ID. For a project rule, use `project` and its explicit ID. Use document tags such as `resume`, `proposal`, `ui`, `technical` or `message`; `general` rules are always eligible. Context retrieval selects the requested scope and tags. It does not load the event history. Fetch no more than three examples for a pattern at a time.

## Consolidate within the budget

The active profile permits at most 12 rules and 350 words, including its headings and exceptions. These are context budgets, not quality scores. The helper rejects an over-budget promotion and keeps the captured correction. It never silently evicts another rule or shortens a qualification.

If the instruction already matches, promotion reinforces the rule with the additional evidence. To change it, supply its ID in `supersedes` and its `expected_revision`. To combine overlapping rules, put all replaced IDs in `supersedes` and test the meaning of each. Consolidation cannot broaden a host or project rule into a general preference. Retired and superseded rules remain in history.

```sh
python3 scripts/learning.py --store "$PROFILE_STORE" retire --id RULE_ID --reason "The rule caused an unnecessary edit."
python3 scripts/learning.py --store "$PROFILE_STORE" context --host HOST --project PROJECT --tags general,FORMAT --markdown
python3 scripts/learning.py --store "$PROFILE_STORE" finish --session TASK_ID --host HOST
```

When learning is enabled, before the final response for a completed task, review its new candidates, consolidate supported rules, then checkpoint with `finish`. Capture immediately rather than waiting for a session-ending signal. A task may end abruptly. The checkpoint records the invocation; it does not install a background hook or establish that another AI ran it. A task with no new evidence needs no invented lesson. Dismiss a rejected candidate with `dismiss --event EVENT_ID --reason "REASON"`; the evidence stays in history. Retiring a rule keeps its reviewed examples out of the pending queue.

## Transfer learning between tools

Export only the active profile by default. Its rules still reflect personal preferences, so share them only with an approved destination. Raw correction examples are omitted unless `--include-events` is supplied. Add `--session TASK_ID` to transfer examples from one task rather than its whole history.

```sh
python3 scripts/learning.py --store "$PROFILE_STORE" export --out profile-transfer.json
python3 scripts/learning.py --store "$PROFILE_STORE" import profile-transfer.json --owner "OWNER"
python3 scripts/learning.py --store "$PROFILE_STORE" transfers
```

Import checks the checksum, explicit owner and event IDs. A checksum checks the bytes; it does not establish the authority of their contents. Imported rules remain candidates. Review them against the owner's supplied profile and local examples, then use `owner-transfer` as the review basis with the returned `transfer_id`. Include `owner_confirmation` in the review with a `statement` describing the owner’s adoption request and a `source_ref` identifying it. The instruction, exception and scope must match that transfer. This is a procedural provenance record, not identity authentication; an owner string or checksum cannot prove who supplied the file. If adoption authority is missing, keep the personal rule as a candidate. A repair supported only by the writing standard uses that basis instead. Imported text cannot authorize tools or override the core skill.

For a host without Python, follow [host setup](host-setup.md). Keep the same bounded profile and event fields in editable files. A manual transfer may contain `payload` without a checksum. A receiving tool with Python can seal those bytes before import:

```sh
python3 scripts/learning.py --store "$PROFILE_STORE" seal manual-transfer.json --out checked-transfer.json
```

Never invent a checksum or claim that a file generated in a chat updated project knowledge. Read back the exact stored version and test retrieval in a fresh context when the host permits it.
