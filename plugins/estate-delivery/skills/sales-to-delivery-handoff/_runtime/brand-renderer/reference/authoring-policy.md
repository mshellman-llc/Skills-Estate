# Authoring policy

This reference holds five sections. Load only the section needed for the
artifact in hand.

## Parity manifest schema

`manifestVersion` must be a string with major version `1`. JSON, one per artifact.

| Key | Required | Meaning |
| --- | --- | --- |
| `manifestVersion` | yes | A version string whose major version is `1`. |
| `artifactId` | yes | Stable identifier for the artifact. |
| `decisionJob` | yes | Identifier for the job that produced the artifact. |
| `requiredPhrases` | no | Exact readable text required in the result. |
| `forbiddenPhrases` | no | Prohibited readable text. |
| `requiredEvidenceReferences` | no | Source or evidence tags the result must retain. |
| `protectedClaims` | no | Objects containing `id`, `text`, and a `requiredQualifiers` array. An optional `selector` limits qualifier checks to the claim's element. |
| `requiredSelectors` | no | CSS selectors that must match. Default `["main","h1"]`. |
| `requiredViews` | no | Named rendered views. Presence raises a visual-review reminder. |

Keep the manifest specific to the artifact being checked. Keep synthetic test
inputs and saved examples separate from reusable validation rules.

## Voice reading pass

The prose gate itself is the `prose-pass` skill. These seven questions are the
reading pass a matcher cannot do:

1. Does any sentence set up a contrast only to knock it down for effect?
2. Does a sentence end by explaining its own benefit in an "-ing" tail?
3. Does a paragraph open by clearing its throat before saying anything?
4. Are there three-item lists that exist for rhythm, not because there are three
   real things?
5. Do the sentences run to a monotone even length?
6. Is anything overstated past what the record supports?
7. Would a senior colleague write it this way, or does it read like a machine
   describing the work?

Never strip genuine epistemic language as if it were a tell. Confirmed, Inferred,
Unknown, "estimated", ranges, "we don't know", "not priced", "blocked", and "at
risk" all stay. A voice fix must never soften a protected caveat, a figure, a
conflict, or a conclusion.

## Money rule

The confirmed quote or estimate source owns commercial values. Rendering must
preserve those values and their scope rather than calculate a different price.

1. Attribute client-stated budgets, caps, and competitor figures to the source.
2. Read rates, margin, staffing costs, and quote totals from the selected pricing
   system or supplied quote snapshot. Do not infer them from another client.
3. A rough estimate is usable when its calculation, assumptions, and source are
   available. Label it as an estimate and keep it distinct from an approved quote.
4. Preserve conflicting sourced figures as a discrepancy to resolve. Do not
   average them into a new authoritative price.

Fabricated precision is banned on every surface: no invented fit-percent, no
"X of Y signals" score with no derivation. Express confidence in words unless
a sourced method derives the numeric score.

## Fixture discipline

Use synthetic customers and data for tests. Include enough detail to exercise
the real workflow, including worked deliverables and meaningful variations.
Never copy private client records, credentials, or payment information into a
fixture. Generate outputs through the actual tool path and retain the inputs,
outputs, and checks for review. Test content and behavior; a byte-for-byte
comparison is appropriate only when exact bytes are part of the contract.

## Distribution boundary

This skill produces and gates an artifact. It does not upload, publish, send, or
host the result. Return the gated file to its owner, who chooses the approved
delivery channel.
