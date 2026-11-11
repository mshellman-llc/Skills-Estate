# Reconcile the scope reference

`scope_reference_validate.py` compares the proposed matrix with captured quote records. It uses stable IDs so punctuation changes cannot merge separate items. The bundled fixtures in `examples/` show both comparison and single-option inputs.

## Source record

The top-level object has `kind` (`export`, `live-capture` or `synthetic`), `system`, `revision`, a timezone-bearing `captured_at`, and `quotes`. These fields record the capture; they do not authenticate a live system. Retain the original connector response or export beside the normalized source.

Each quote contains:

| Field | Content |
|---|---|
| `id` | The quote's stable identifier. |
| `full_items` | Every scope item, including deselected and optional work. |
| `active_item_ids` | IDs from the active-only read. Every ID must occur in the full list. |
| `active_snapshot_id` | The ID reported as active by the timeline list. |
| `snapshots` | The snapshots needed for the reference, retaining their own IDs. |

Each item has `id`, `name`, `category`, nonnegative `hours`, an explicit Boolean `optional`, and a `description` or `effort_basis`. The same item ID across quotes must name the same item and category. Quote-specific IDs need an explicit, reviewed mapping to common IDs before normalization. Preserve that mapping with the original responses. A name similarity is insufficient to establish identity.

Each snapshot has `id`, `label`, `currency`, `revenue`, `weeks` and `hours`. The currency is a three-letter code. All numeric values must be finite and nonnegative. Preserve decimal currency values. A newer inactive snapshot may remain in the capture; it is not automatically displayed.

Optional `notes` contain source-supported scope conditions. The builder displays all of them. Keep internal retrieval comments outside this field.

## Presentation record

The presentation has `title`, `client`, `intro`, `options` and `matrix`. `rounding` defaults to `1`, meaning exact currency display; `1000` adds an approximate headline rounded half-up to the nearest thousand and retains the exact amount.

An option has `quote_id`, `name`, `summary` and a `snapshots` list. Copy the fields of each requested source snapshot exactly. Include the active snapshot. Additional variants must exist in the capture and retain their actual labels, revenue, duration and staffing hours.

Each matrix entry has `id`, exact `name`, exact `category`, `description`, `description_basis` and `cells`. The basis identifies `quote_id` and `field` (`description` or `effort_basis`) from a captured occurrence of that item. Preserve a supplied source document as an evidence field in the normalized capture when it is the description authority.

Cells are keyed by quote ID. Each has `state` and `hours`. States are `in`, `optional`, `available` and `out`. An absent item has `hours: null`; it must not inherit another option's estimate. Every presentation item has a cell for every option. The matrix contains the union of the supplied quotes' scope, with no omissions or extra rows.

## Failure behavior

Reconciliation stops on duplicate IDs or JSON keys. It rejects unknown active items, an absent active snapshot, an unsupported variant, inconsistent identity and missing evidence text. Any mismatched scope cell or snapshot value prevents output. Existing HTML and receipt files are never overwritten; use a new attempt directory.

The successful receipt records counts for each state and the source revision. It also binds the input files, profile and HTML with SHA-256 hashes. It establishes agreement with those exact files. Review original-source normalization and description meaning separately before making a current-client claim.

## Compatibility API

Older callers may still import `validate(file_items, source_items, prefix_aliases=None)` and `present_counts(items)`. The legacy shape is `name -> {hours, states}`. That API now rejects normalized-name collisions and unknown states. It supports a common hours value only; use the new source/presentation contract when hours differ by option. `present_counts` means included plus optional plus available. It is not the included count.
