# Local files and artifacts

Resolve an absolute destination before writing. Preserve existing user content
and unrelated files. For replacements, use the application's native save or an
atomic write when practical.

A file existing on disk proves only `saved-locally`. Verify the artifact in the
application or parser that will consume it. For visual deliverables, inspect the
rendered result. For structured data, validate the schema and reopen the saved
file. A local file does not prove a Drive upload, publication, installation, or
availability to another person.

Report the absolute path, validation performed, and every expected surface that
remains unchanged.
