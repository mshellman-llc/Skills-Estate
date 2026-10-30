# Specification inputs

Before building or approving an offering suite, obtain explicit paths to the
caller's approved specification, manifest JSON Schema, qualifier JSON Schema,
and stage-gate workbook. Keep these project inputs outside the reusable package.
Record their versions, approving source and file hashes in the project run record.
A filename, a copied example or the caller's access to a file does not establish
that it is the current approved policy.

Read the specification's shared rules and the artifact sections needed for the
requested work. Validate the manifest and qualifier against their supplied schemas
with a validator that supports the declared schema dialect. Record the validator,
inputs and results. Do not retrieve external schema references without authorized
access; report an unresolved reference when that access is unavailable.

Compare the supplied artifact matrix, shape requirements, formats, numbering,
ROM conditions, dependencies, gates and naming rules with `scripts/spec_shapes.py`
and the planner. Compare the workbook with the specified stage-gate requirements.
Preserve legal, commercial and role rules from the approved project sources.
Do not apply a former organization's convention merely because it appears in the
preserved compatibility model.

If any required input is missing, or the approved rules differ from the model,
report the specific gap. You may inventory the folder and run a labeled diagnostic
plan, but do not call it conforming, copy an invented workbook, silently change
rules or mark the suite ready. A different specification needs a reviewed adapter
change before the planner can represent it accurately.

The current scripts check the preserved version 1.1 model and manifest assertions.
They do not read these external authorities, validate JSON Schemas or inspect the
contents of deliverables. Their `spec_authority` result remains unverified even
when all modeled artifacts have gate dispositions. Retain separate evidence of
specification review, schema validation and rendered-content acceptance before
requesting release approval. No script result authorizes publication.
