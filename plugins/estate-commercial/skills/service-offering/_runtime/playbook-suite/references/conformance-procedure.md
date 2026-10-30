# Conformance run

Bringing an existing playbook onto the spec. Applies to any playbook authored before the
current spec. Run it deliberately: the first playbook through this process sets the de facto
standard for the ones that follow.

## Order

**1. Freeze the spec.** Nothing regenerates against a moving definition, so pin the spec
version before you start. Obtain the explicit inputs and complete the authority checks
in [spec-inputs.md](spec-inputs.md). The bundled scripts check the preserved 1.1
model only; a successful run is not current specification acceptance.

**2. Inventory.** Run the audit against the playbook folder:

```bash
python3 conformance_audit.py PLAYBOOK_DIR --manifest manifest.json
```

If no manifest exists, run with `--infer` to generate a draft from filenames, then correct
it by hand. An inferred manifest is a starting point, never a source of truth.

**3. Classify each artifact.** Four outcomes, and the third is the one people get wrong.

| Outcome | Meaning | Action |
|---|---|---|
| Conforming | Right artifact, right format, right brand, gates recorded | Leave it |
| Repairable | Right structure, wrong detail such as a stale figure or a role name | Edit in place |
| Regenerate | Wrong structure or off-canon brand | Rebuild from a manifest |
| Obsolete | The artifact no longer exists in the spec | Archive, do not delete |

Retrofitting a differently structured deck costs more than rebuilding it. When the structure
is wrong, regenerate.

**4. Reconcile every number to the quote.** Check figures against the live quote and its
active timeline snapshot as of today, not against whatever the file was built from. A
mismatch is a blocking finding: flag it, adjust neither side unilaterally.

**5. Gate everything.** All three gates per artifact, dispositions written into the manifest.

**6. Promote.** Once conforming, lift the artifact set into the pattern references so later
playbooks copy a correct example as the canonical DDOC structure.

## Preserved version 1.1 corrections to verify with the current specification

These are compatibility rules, not universal policies. Apply each only when the
caller's approved specification confirms it; otherwise record the conflict and
leave the source unchanged.

- Any Pricing Sheet spreadsheet is obsolete. Pricing is the quote.
- Any internal Deal Desk document is obsolete. Deal Desk reviews the quote, SOW, and DDOC.
- Any per-option DDOC set collapses into one DDOC covering all options.
- Any artifact rendered on an old palette regenerates on the current brand tokens.
- "Accountable Executive" becomes "Client Services Executive (CSE)". "Account Executive"
  stays as it is; the two roles are different and both are live.
- A three-slide DDOC is below the floor and regenerates against the full slide set.
