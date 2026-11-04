# Profile schema

The compact runtime profile a build produces. One JSON file per person, stored
outside this repository. Field order below is the field order in the file.

```json
{
  "person_id": "string, opaque handle chosen at build time, not a real name",
  "authorization": {
    "granted": true,
    "granted_at": "ISO 8601 timestamp",
    "scope": "what the person authorized this profile to be built from"
  },
  "revoked": false,
  "last_confirmed": "ISO 8601 timestamp",
  "history": [
    {"at": "ISO 8601 timestamp", "change": "one line, what changed and why"}
  ],
  "routing": {
    "authorship_trigger": "apply only when this person is author or speaker",
    "modes": ["written", "spoken"],
    "surfaces": ["chat", "email", "document", "brief", "deck", "talk-track", "call"],
    "audiences": ["peer", "internal-group", "leadership", "client", "prospect", "public"],
    "relationships": ["new", "transactional", "established", "close"],
    "jobs": ["inform", "request", "correct", "persuade", "decide", "set-boundary", "facilitate", "support"]
  },
  "base_profile": {
    "written": {
      "core_tendencies": [
        {"pattern": "string", "confidence": "high|medium|low", "provenance": "authored|templated-edited", "sources": 3}
      ],
      "insufficient_evidence_for": ["dimension names with too little signal"]
    },
    "spoken": {
      "core_tendencies": ["same shape as written.core_tendencies"],
      "insufficient_evidence_for": []
    }
  },
  "channel_overlays": {
    "<surface>x<audience>x<job>": {
      "adjustment": "how this combination changes the base profile",
      "confidence": "high|medium|low",
      "sources": 2
    }
  },
  "conflicts": [
    {"dimension": "string", "readings": ["reading A", "reading B"], "resolution": "unresolved|resolved:<note>"}
  ]
}
```

## Field rules

- `person_id` never holds a legal name, email, or handle traceable outside the
  profile store. The store's access control does that job.
- Every entry under `core_tendencies` and `channel_overlays` names `sources`
  (a count, not the raw text) and `provenance`. A pattern with zero
  `authored`-provenance sources is not eligible for the profile.
- `insufficient_evidence_for` is not an error state. A profile can ship with
  gaps; the runtime falls back to plain, unstyled drafting for a routed
  combination that has no confirmed pattern rather than inventing one.
- `conflicts` stays even after a profile update unless the person resolves it
  directly — a later build must not silently pick a side.
- Deleting a profile removes this file and the raw evidence store; it does not
  set `revoked: true` and leave the data in place. `revoked: true` is for
  "stop applying this automatically," a lighter, reversible action.
