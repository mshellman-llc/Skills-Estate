# Generate a permission set from local metadata

`gen-permset.py` builds permission-set XML from an SFDX project's files and a project-specific JSON configuration. It works without Salesforce CLI, credentials, or an org. It derives applications, Apex classes, Visualforce pages, object and field permissions, record types, tabs, custom permissions, and custom metadata type access. Flow access is optional.

The generator keeps the permission set consistent when separate branches add metadata. Regenerate after combining those changes, review the grants, and validate that exact commit against the intended org before deployment. Local XML generation establishes neither platform acceptance nor a user's effective access.

## Install and configure

Copy `gen-permset.py` into the project's `scripts/` directory. Run from the project root:

```bash
python3 scripts/gen-permset.py --init
```

This creates `config/permset-gen.json` without overwriting an existing file. Set `api_name`, `label`, and the access rules for the project. `--help` prints the complete configuration reference. An optional npm configuration is:

```json
{
  "scripts": {
    "permset": "python3 scripts/gen-permset.py",
    "permset:write": "python3 scripts/gen-permset.py --write"
  }
}
```

Python 3 and local source files are sufficient for preview and check mode. Git is also required for writing into a linked worktree. No command in this tool connects to Salesforce.

## Preview, check, and write

| Command | Behavior |
|---|---|
| No flags | Compare generated content with the configured output; write nothing. |
| `--fail-on-drift` | Return exit 3 when check mode detects a difference. |
| `--out /tmp/new-preview.xml` | Write a new preview outside SFDX project trees; refuse an existing file or symlink. |
| `--write` | Write the generated permission set only in a verified linked Git worktree. |
| `--tree PATH` | Select the SFDX project for reads and any write. |
| `--config PATH` | Read another JSON configuration; an absolute external configuration is allowed. |
| `--init` | Create a new configuration inside the selected project. |
| `--help` | Show the workflow and configuration fields. |

`--write`, `--out`, and `--init` are mutually exclusive. Invalid inputs or refused actions return exit 2. A successful check returns exit 0 unless `--fail-on-drift` is used. Inspect the printed drift result when using plain check mode.

The target follows `--tree`; otherwise it is the nearest `sfdx-project.json` above the working directory, then above the script. A main checkout remains a refused write target even when the command runs from a worktree. Missing Git or unreadable Git topology also refuses a write.

For a coordinated build, contributors run check mode and report missing grants. The person integrating the change regenerates in the target worktree, reviews and commits the generated file, and reruns checks against that commit. For a solo build, the same person performs both steps. A hand edit to generated XML will be replaced by the next generation; put intended access changes in the source or configuration.

## Define access deliberately

- `standard_object_access` grants CRUD on named standard objects. Standard-object fields can receive field permissions without this list granting object access; review both levels.
- `no_delete` withholds the generator's Delete grant for matching objects. Other permission sets and profiles can still grant Delete.
- `read_only` makes matching `Object.Field` entries non-editable in this permission set.
- `exclude_objects`, `exclude_fields`, `exclude_tabs`, and `exclude_apex_classes` suppress their respective sections. Excluding an object's CRUD does not implicitly remove its field permissions; use `exclude_fields` when that is intended.
- `standard_tabs`, `user_permissions`, and `extra_custom_permissions` add explicit grants that cannot all be inferred from source files.
- `derive` switches individual derived sections on or off. Values must be JSON booleans; unknown section names are refused.
- `field_permissions_for` selects object kinds receiving FLS. Defaults are standard and custom objects. `custom_settings` defaults to `skip`; changing it to `object` affects CRUD, while FLS needs its own configuration.

Lists documented as patterns accept globs. Literal standard objects can receive configured access even when no object directory exists. Exclusions take precedence over those explicit standard-object grants.

The generated permission set grants access; it cannot revoke access from another permission source. Test effective access with an appropriate user in the target org before claiming that a field or operation is restricted.

## Field classification and package handling

The restored implementation preserves these rules: omit MasterDetail and universally required fields; make formula, roll-up summary, and AutoNumber fields read-only; make other supported fields editable unless configuration overrides them. Offline tests verify that the generator implements those rules. Historical source notes reported org testing, but this repaired version has not been deployed to an org.

Custom settings and unsupported field-permission kinds are reported when skipped. Custom metadata type access uses its own section. Flow access defaults off; when enabled, the generator includes screen and autolaunched flows without a trigger type. Confirm the generated permissions against the target platform before enabling optional grants.

Both standard `package/main/default` and flat package layouts are supported. A fresh worktree with no metadata yet uses the standard layout. Fields split across multiple packages are combined. Identical duplicate components are collapsed; conflicting duplicates are refused. Same-named record types on different objects remain separate.

Project paths must stay inside the selected tree. Package symlinks cannot lead outside their package. Malformed metadata XML and unreadable files stop generation. Labels and descriptions are XML-escaped. Output elements follow the generator's ordered PermissionSet sections.

## Resolve a generated-file conflict

Preserve the conflicting versions for review, resolve the source metadata and configuration first, then regenerate inside the worktree. Compare the result with the intended grants, commit it, and repeat the project checks. Do not infer that a conflict-free generated file has passed a Salesforce deployment validation.

## Verification and retained output

Run the skill's `scripts/gen_permset_selftest.py` for 46 offline checks covering classifications, write targets, fresh and flat layouts, XML shape, idempotence, drift, and configuration errors. The estate's `tests/test_permset_behavior.py` exercises both shipped copies, including split packages, conflicting metadata, XML escaping, file preservation, invalid arguments, and failed Git checks.

For an estate run, use `tools/run_preserved_test.py` with a new attempt directory. It retains synthetic projects, generated XML, and console results, including failures. These checks do not make Salesforce API calls. Keep real org identity receipts and private project metadata outside the reusable skill package.
