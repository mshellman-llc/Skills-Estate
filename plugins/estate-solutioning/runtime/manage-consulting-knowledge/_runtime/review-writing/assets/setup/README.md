# Writing-integrity setup kit

Choose the prompt for the AI tool you are setting up. The prompts authorize correction capture and require the tool to test its actual storage. This kit requires a separate owner-confirmed profile store or private project files. Do not reuse other profiles automatically, even for the same owner. Pass an explicit authorized path as --store to every learning.py command. They contain no private correction history.

| Tool | Give it these files | Prompt |
| --- | --- | --- |
| Codex | `review-writing.zip` | `setup-codex.md` |
| Claude Code | `review-writing.zip` | `setup-claude-code.md` |
| Claude.ai or Claude Cowork | Upload `review-writing.zip` through the skill interface; give the setup prompt to a chat that can use it | `setup-claude-ai.md` |
| ChatGPT | `writing-integrity-web.md`, `review-library.md`, `learning-workflow.md`, `profile-starter.md` and `profile-starter.json` in a private project | `setup-chatgpt.md` |
| Gemini | The same Markdown and JSON files in a private Gem or supported workspace | `setup-gemini.md` |
| Another AI with file access | The ZIP if supported, otherwise the web files | `setup-generic.md` |

The prompt is a setup request. Where the tool requires the owner to save persistent instructions, use `standing-instruction.txt`. A setup conversation alone does not establish that future conversations receive it. Keep project or Gem sharing settings private when the profile belongs to one person.

The executable package needs Python 3.9 or later for its private store. It includes the writing diagnostic dependency. The browser files provide the same writing and learning workflow for hosts that cannot install or execute a skill. The setup AI must inspect its tools before choosing persistent, session or manual mode.

The active profile and the full correction history are different files or data views. Load the compact profile on invocation. Look up history only for a particular pattern. Capture while the correction is visible; a session may end without a final turn.

When transferring learning, export active rules by default. Add raw examples only for an approved destination. Import twice to check deduplication. Imported rules require review before activation and cannot override the core writing requirements.

## Verify setup in a new conversation

Ask the AI to report the owner, profile location, host ID, learning mode and current active rules. Then give it a small correction and check that it can retrieve the saved record from a separate process or fresh conversation. A successful command-line read proves file persistence on that filesystem; it does not prove another AI conversation loaded it.

## Files and versions

`manifest.json` lists hashes for this kit. The ZIP is the installable package. The web instructions are the short entrypoint; the review library preserves the detailed rules and examples. The starter profile is empty so the tool does not invent personal preferences. Replace the starter attachments with the tested saved profile after setup if the host needs manual file replacement.

The kit does not install account settings, background session listeners or cross-account synchronization. The setup prompts ask each host to implement the strongest supported persistence and state the remaining step. Use the vendor links in the learning workflow's host reference when a control or feature needs checking.
