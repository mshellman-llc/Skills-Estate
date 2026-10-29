# Skills Estate

Author skills in `skills/` and shared rules in `policies/`. `build/` and `dist/` are generated. Never edit installed or account-synced copies as the source of truth.

Apply [the shared workflow](policies/workflow.md) and [writing standard](policies/writing.md) while authoring. These policies apply across source modules; portable packages link them once from their top-level entrypoint.

Read the requested skill and its referenced files before changing it. Preserve specialized workflow decisions and supported resources. Keep company identities, private client records, credentials, legal clauses, and payment details out of reusable skills. Branding comes from `policies/brand.md` and the current project's confirmed profile.

Use separate checkouts for concurrent workers and assign one owner per source path. Preserve dirty work. Keep temporary run evidence outside distributable packages; reuse the existing task record rather than creating another folder.

Run `python3 tools/estate.py validate`, `python3 -m unittest discover -s tests -v`, and `python3 tools/estate.py sync` before delivery. After source or dependency changes, refresh both candidate build and ZIPs from a stable source tree. If that is blocked, report the stale outputs and exact remaining command; do not describe them as current. `sync` refreshes candidate build and ZIPs only. Git hooks never build or install. Use `status` to inspect source, build, ZIPs, pinned installations, and account gaps. Before rebuilding a checkout with legacy mutable installations, use `pin-installed` to preserve their existing bytes. Everyday promotion requires the reviewed `--expected-source` hash and completed release gates; do not promote a source-restoration candidate. `install` refuses conflicts; `adopt` is a separate reversible migration with backups. Never overwrite `synced/` or platform-managed plugins.

The user owns this private repository. Existing source archives retain their history. Do not add a distribution license or claim authorship of imported material without evidence. Local install checks do not prove account upload, runtime discovery, or deployment.
