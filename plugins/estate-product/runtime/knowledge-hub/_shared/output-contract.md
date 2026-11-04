# Output contract

Deliver the artifact or operational result the user requested. A deck request
finishes with a usable deck; a knowledge update finishes with retrievable records;
a deployment request finishes with evidence from the target environment.
An accompanying report cannot satisfy those outcomes.

## Produce and verify the requested output

1. Identify the required format, audience, destination, inputs, and acceptance
   criteria before building. Use the producing skill's specific workflow and
   schema. Preserve required fields, calculations, decisions, and source links.
2. Save the actual output in the requested destination, or the project's
   `artifacts/` directory when no destination was specified. Use descriptive
   filenames that distinguish the artifact, version, and format.
3. Open or read back the finished result. For rendered files, inspect the
   rendered pages or slides as well as the underlying data. Exercise interactive
   controls. For operational work, check the resulting state in the target.
4. Fix failures and repeat the affected checks. A missing dependency requires a
   supported replacement, configuration, or workflow change that preserves the
   requested capability. Describe any remaining dependency precisely; do not
   label the capability ready while its required behavior remains untested.
5. Deliver or link the usable output. State where it exists and what was tested.
   Keep local creation, installation, publication, and live operation distinct.

## Retain evidence

For an implementation, migration, test, or release, save a supporting run record
with the input references, commands or actions, expected and observed results,
remaining limitations, and paths to the produced files. A compact JSON record or
Markdown index is sufficient; a knowledge base's `INDEX.md` can serve this role.
This record supports the output and does not replace it.

During estate verification, retain every generated test output, input fixture,
log, and preview, including failed attempts. Put attempts in separate directories
so a rerun cannot erase the evidence. Use synthetic fixtures for distributable
examples. Keep private source material and credentials out of release packages.

For ordinary content tasks, include sources and material assumptions in the
artifact or a short companion note when needed. Do not add a generic executive
report to a task that does not need one.

## Evidence and persistence

- Distinguish sourced facts, user-provided facts, and inferences.
- Preserve enough source detail to retrieve the evidence again.
- Reconcile figures with their stated source and record material assumptions.
- Never record secrets, credentials, access tokens, or irrelevant private history.
- If the environment cannot persist or deliver the requested file, state that
  limitation and provide the recoverable content available. Chat text is not
  proof that a file was created, installed, or uploaded.

The skill's own output schema and acceptance criteria apply in addition to this
contract.
