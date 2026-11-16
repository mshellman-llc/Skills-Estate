# Skill names

Name each public skill for the task a user wants it to perform. Use a short action followed by its subject: `build-deck`, `plan-sprint`, `review-writing`. Add a platform or domain when it distinguishes the task, as in `configure-salesforce-project`.

Use lowercase ASCII letters, digits and single hyphens, with a maximum of 64 characters. Start and end with a letter or digit. Match the source folder, frontmatter name, catalog entry, package folder and invocation identifier for the same public skill. Keep the identifier stable after release.

Choose a name that covers the workflow's actual scope. Distinguish adjacent tasks and check the catalog and installed host for collisions. Prefer recognizable words to abbreviations. Keep employer names, personal systems, creation tools and origin stories out of identifiers. A product name belongs in an identifier only when that product is the subject of the task.

Supporting components can use a role name such as `brand-renderer` or `evidence-core`. They remain internal resources. A task mode uses an action name and stays within its owning public workflow. Do not expose an internal module as a second public skill merely to make its name visible.

Descriptions state the capability and the requests that select it. Keep personal context, release history and implementation commentary out of the description. Preserve useful distinctions between related workflows.

When renaming, update the source, catalog, runtime graph, routers, examples, UI metadata and tests together. Rebuild packages and generated pages. Use the managed installation inventory to retire old links; preserve divergent or unmanaged copies for review. Verify discovery and invocation in each target host after an authorized installation.

The format follows the [Agent Skills specification](https://agentskills.io/specification). The action-led convention follows [OpenAI's authoring guidance](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md#skill-naming) and is one of the patterns accepted by [Anthropic's authoring guidance](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#naming-conventions).

## Commit messages

Use `type(scope): action and result` for new commits. Choose a stable scope such as `skills`, `catalog`, `packages`, `map` or `docs`; use `feat`, `fix`, `refactor`, `docs`, `test`, `build` or `chore` for the change type. Write the subject in the imperative and keep it brief. Use the body for the problem, resulting behavior and relevant validation. Keep chat transcripts, personal workstation paths, generation-tool commentary and creation stories out of commit messages. Preserve accurate human authorship and required third-party notices.
