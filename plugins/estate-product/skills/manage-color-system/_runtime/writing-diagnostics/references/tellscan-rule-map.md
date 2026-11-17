# How this checker relates to tellscan

`writing_check.py` in this skill is the authoritative writing check for files in a Skills Estate checkout. tellscan is a separate personal scanner that runs as an assistant hook on chat replies and on files written outside the estate. It is not part of the estate and is not versioned here. When the two disagree about an estate file, this checker governs, and `tools/verify.py` reports its findings for the files a branch changed.

The table maps tellscan rules to the rules in `prose_check.py` by their stated intent. A match means the two rules target the same pattern; it does not mean they flag the same sentences. tellscan's `triad` rule, for example, flags any list of three, while `C7-triad` flags only three evaluative adjectives. True three-item lists therefore pass here and get flagged there.

| tellscan rule | Covered here by | Notes |
|---|---|---|
| `triad` | `C7-triad` | Narrower here, by design |
| `not-x-but-y`, `m-antithesis` | `C2-antithesis` | |
| `fragment-stack` | `C6-fragment-stacking` | |
| `copula-avoidance` | `C18-copula-avoidance` | |
| `em-dash` | `em-dash` | |
| `hedge-stack` | `C21-hedge-verb`, `C23-trailing-hedge-adverb` | Partial |
| `intensifier`, `significance` | `C19-gravity-marker` | Partial |
| `vocab-marker` | `house-banned-term` | The word lists differ |
| `bold-lead-bullets`, `title-case-heading`, `emoji-heading`, `rule-before-heading` | none | Formatting rules; none are ported yet |
| `signpost`, `drumroll`, `stock-transition`, `trailing-participle`, `vague-attribution`, `insider-reveal`, `vocab-landscape`, `chat-residue` | none | Not ported yet |
| `m-*` and `u-*` rules | none | Personal voice and learned corrections; they stay in tellscan |

A rule with no equivalent here is a candidate to port, not a gap to fill by running both checkers on estate files. Port a rule with a selftest case that shows what it flags and what it leaves alone.
