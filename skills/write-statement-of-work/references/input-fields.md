# Input fields that fill contract tokens

Each token in the contract profile's clause text has its own source field. No token borrows another token's field.

| Token | Source | Unresolved when |
|---|---|---|
| `{PROVIDER}` | profile `provider.legalName` | absent |
| `{CLIENT}` | quote `projectContext.clientLegalName` | absent or empty |
| `{N}` | profile `startWindowDays`, a positive whole number of days | absent |
| `{DATE}` | quote `projectContext.signingDate`, an ISO date | absent or empty |
| `{TOTAL}` | quote `projectSummary.totalValue` | absent |
| `{UPFRONT_PERCENT}` | profile `upfrontPercent` | absent |
| `{UPFRONT}` | total value times `upfrontPercent` | either is absent |

- `clientLegalName` is the contracting party in the parties paragraph, the notices table, the signature block and the contract verifier's client identity check. `accountName` stays the display name on the cover and in narrative text. When the legal entity is not known, leave `clientLegalName` out: the build flags it, the resolution log records it as flagged, and `--draft` shows `[FLAG: ...]` in the document. Never copy `accountName` into it to clear the flag.
- `startWindowDays` is the number in a clause such as "if the client does not start within {N} days of signature". It is not the engagement duration (`projectSummary.durationWeeks`).
- `signingDate` is the date the agreement is signed. `returnBy` is the date the offer expires, and no token reads it.

An unresolved field stops a build unless `--draft` is given. `verify_contract.py` reports each one as its own finding.
