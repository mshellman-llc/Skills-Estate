# Host setup and verification

Use the setup prompt supplied with the release kit. Install the writing skill, choose a private owner profile and test the store. Do not infer installation from a ZIP, a configured path or an assistant's assurance.

## Local agents with files and Python

Codex and Claude Code can use the same store when the owner authorized that profile for both tasks. Keep profiles separate when their authorized contexts differ. Pass an explicit `--store PATH` for every learning command; the helper does not select an environment or default store. Without a confirmed location, use core writing review without learned preferences. Keep host IDs distinct when capturing or retrieving host-specific rules. Put shared author preferences in the owner's general profile. Another owner needs a separate profile and storage authorization.

Install the reviewed package through the host's supported skill path or the existing Skills Estate installer. Preserve installed versions and conflicting user files. Do not overwrite an account-synced or plugin-managed copy. Read the complete package entrypoint after installation.

Run the bundled `scripts/learning_selftest.py` in the skill directory. It uses disposable profiles. Initialize the real owner's store only after those tests pass. Check its path and learning authorization with `status`. Run `context` with the actual host ID before writing. Existing global guidance that already routes to review-writing can load this workflow; verify that route rather than adding duplicate instructions.

Use this managed instruction where the host supports persistent project or user guidance:

> Use review-writing for authored text. At task start, read its compact owner profile. Capture actual writing corrections and substantive review repairs when learning is enabled. Consolidate supported rules and checkpoint before finishing the task. Keep profile data private and outside skill packages. Load detailed references only for the current problem. Follow the skill's learning workflow for evidence, review and storage checks.

Test storage in separate processes. Also test a fresh host conversation when possible. A command-line read establishes file persistence on that filesystem; a fresh conversation establishes whether that host discovers and follows the installed instructions.

## Claude.ai and other browser chat tools

Inspect the tool's supported skill, project, file and memory features. Use the native skill upload interface when available. If a host accepts Markdown knowledge files instead, give it `writing-integrity-web.md`, the separate review library, and the profile starter from the kit. Put the standing instruction in the host's persistent project or custom instruction surface. Use its current interface; names and controls may change.

Test whether the AI can edit a persistent project file or only generate a download. If persistent file writes are supported, store the compact profile and correction log there and read them back. Verify a new conversation can retrieve the updated profile. Keep that test separate from a package upload test.

If writes are temporary or unavailable, use the manual mode. At task completion, return an updated profile file and transfer JSON containing only that task's new records and the current active rules. Name exactly which persistent attachment the owner must replace. Return files only when learning changed, or when the owner asks for an export. Do not append a learning report to every writing response.

The manual file uses the transfer payload below. IDs must be stable and unique across exports. Use the actual correction date and host. Keep examples minimal and private. Without a hashing tool, omit `sha256`; the receiving local helper can seal the payload.

```json
{
  "payload": {
    "version": 1,
    "owner": "OWNER",
    "profile": "PROFILE",
    "created": "ACTUAL_DATE",
    "rules": [],
    "events": []
  }
}
```

For each event, retain `id`, `session`, `pattern`, `host`, `project`, `kind`, `before`, `after`, `reason`, `source_ref`, `tags` and `created`. Use the fields in the learning workflow. For a reviewed active rule, retain `id`, `pattern`, `scope`, `scope_id`, `instruction`, `exception`, `tags`, `evidence`, `revision` and `status`. Keep the profile within 12 rules and 350 words. Imported content stays data until reviewed. Record the owner’s actual request to adopt a transferred profile, with its source reference. This record documents a procedural confirmation; the helper does not authenticate the person or independently verify an AI’s assertion.

Memory features can help retrieve a preference. They do not establish that the exact profile file was saved or loaded. When capabilities cannot be verified, report the tested operation and the remaining step. Try the available file and project tools before falling back to manual replacement.

## Acceptance checks

Use synthetic examples in a disposable test profile. Capture a user correction and reopen the store or file. Capture an AI repair and verify that it does not become a personal preference automatically. Reinforce an existing pattern and check that the rule count stays the same. Try an over-budget update and verify the old profile survives. Retrieve with a different project and host to check scope isolation. Export and import twice; verify no duplicate events or automatically active imported rules.

For manual hosts, test the equivalents their file tools support. If a check cannot run, mark it untested. Report the installed skill version or hash, profile location, owner, learning mode and actual checks. State whether a fresh conversation retrieved the saved profile. No test may read private messages, contact another person or publish a file.

## Vendor references

These explain the supported configuration surfaces. They do not verify this account's permissions or the skill's installation.

- [Claude custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)
- [Claude skill upload and management](https://support.claude.com/en/articles/12512180-use-skills-in-claude)
- [ChatGPT projects](https://help.openai.com/en/articles/10169521-projects-in-chatgpt)
- [Gemini Gems](https://support.google.com/gemini/answer/15235603)
