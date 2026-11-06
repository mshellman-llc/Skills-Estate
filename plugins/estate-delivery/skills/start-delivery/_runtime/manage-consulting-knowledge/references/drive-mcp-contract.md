# Google Drive adapter contract

Use this contract when the manifest declares Google Drive as primary. A local
folder or configured sync mount uses the local runtime instead. Available tools
vary by host and version; inspect their schemas in the current session before
planning calls. The helpers in `hub_resolver.py` plan operations and never execute
a network request themselves.

## Detect separate capabilities

Check search, content read, create, metadata update, and content replacement
independently. A metadata response is not a content read. A tool named `update`
may only rename or move a file. Confirm its content argument and existing-file
identifier before treating it as a content updater.

`detect_capabilities` recognizes the legacy adapter's tool names. Other schemas
need an explicit mapping. Do not treat this static mapping as a live audit.

## Resolve identity

Search actual folders and retain returned IDs. Confirm the client and the
opportunity or engagement before selecting a canonical record. Follow every
pagination token for the bounded query before concluding a record is absent.
Use MIME filters for document types and the connector's actual parent filter.
Never construct a Drive file ID or infer one from a title.

The legacy query schema accepts forms such as:

```text
title contains 'Example Manufacturing' and mimeType = 'application/vnd.google-apps.folder'
parentId = '<confirmed client folder id>' and title = 'AI Knowledge Hub'
```

`choose_folder` refuses equally plausible identities. `find_hub` refuses duplicate
hub folders under the confirmed parent. Normalize actual search responses into
these helpers' `id`, `title`, `mimeType`, and `parentId` fields when the host uses
a different response shape.

## Create actual Markdown

For the legacy `create_file` schema, `plan_create_markdown` supplies
`contentMimeType: text/markdown` and `disableConversionToGoogleType: true`.
These prevent conversion into a native document on that adapter. Use the
corresponding fields from the current schema on other hosts. After creation,
verify the returned MIME type, file ID, parent, and content.

Do not create another same-title file to bypass an unsupported content update.
Do not delete and recreate a canonical file: that can discard history and links.

## Update the existing file

Configure `ContentUpdateContract` only after reading the available tool schema.
It maps the actual tool name, existing-file ID argument, content argument, and
optional version argument. Pass the contract, canonical file ID, and observed
version to `plan_record_write` or `plan_canonical_write`. A boolean capability
flag alone cannot enable an update.

When the provider supports a conditional version or ETag, require the observed
version in the write. Without that feature, reread immediately before writing,
compare against the version originally read, and coordinate a single writer;
this does not provide an atomic compare-and-swap guarantee.

Execute the returned plan through the actual tool, then read back the same file
ID and compare the intended content. Only then report `written-and-confirmed`.
If required mirrors have not been updated, report
`written-primary-mirrors-pending` and name them.

When no content updater is available, an explicitly configured local primary can
support the complete local workflow. Changing primary authority is a deliberate
migration, never an automatic fallback. Otherwise return the exact target and
merged content as `patch-returned`, with no persistence claim. Resolving the
missing integration remains unfinished work for a task that requires a live
Drive update.

## Scope and proof

Operate inside the confirmed hub tree. Sharing, deletion, and moving canonical
files are separate actions requiring their own authorization. Preserve
superseded content and report primary and mirror outcomes separately.

Local adapter tests prove planning and refusal behavior. They do not establish
that a particular account has Drive access or that a cloud write succeeded.
