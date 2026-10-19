# Skills Estate

Author skills in `skills/` and shared rules in `policies/`. `build/` and `dist/` are generated. Never edit installed or account-synced copies as the source of truth.

Read the requested skill and its referenced files before changing it. Preserve specialized workflow decisions and supported resources. Keep company identities, private client records, credentials, legal clauses, and payment details out of reusable skills. Branding comes from `policies/brand.md` and the current project's confirmed profile.

Run `python3 tools/estate.py validate`, `python3 -m unittest discover -s tests -v`, and `python3 tools/estate.py build` before delivery. Use `status` to inspect installed copies. `install` refuses conflicts; `adopt` is a separate reversible migration with backups. Never overwrite `synced/` or platform-managed plugins.

The user owns this private repository. Existing source archives retain their history. Do not add a distribution license or claim authorship of imported material without evidence. Local install checks do not prove account upload, runtime discovery, or deployment.
