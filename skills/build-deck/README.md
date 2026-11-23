# Deck builder

Build a proposal or briefing through the [complete staged workflow](SKILL.md). Save the argument and slide plan before rendering. The bundled HTML route produces a standalone deck with selectable text and print styling. PowerPoint uses the available presentation tool.

Read [HTML production](references/html-production.md) for the input contract and build command. Select branding through the canonical profile. Keep the final deck and its stage files together.

Use [Visual argument](references/visual-argument.md) to choose the narrative and the relationship each slide must explain. The [reconciliation example](examples/reconciliation-narrative.json) includes a lost-response sequence, recovery branches, a finance review path, an annotated exception record and a service boundary. It is a proposed design using synthetic records, with no measured business results or live integration claims.

The HTML renderer supports connected diagrams, sequences, record specimens and nonnegative bar comparisons, alongside tables and text. Its browser checker saves desktop and narrow-screen views and a landscape PDF. Review every slide against its audience question after rendering. A passing clipping check does not establish that the explanation works.

## Scope claims in a deck

A pitch, briefing or decision deck that says what is in and out of scope makes
contract-scope claims. `review-deliverable` fails closed on every such claim
(assertion kind `contract_scope`) until a control backs it, and it will not
release a record that declares `contract_scope` with no scope control run.

### The choice

`review-contract-scope` is the statement-of-work control. It ships in
`estate-solutioning` and not in `estate-pursuit`. A deck built here could never
meet "do not present the artifact as finished until every check that applies has
passed". Two fixes were possible.

1. Bundle `review-contract-scope` into build-deck as a runtime module. Rejected.
   It audits the structure and language of a contract: de-slop, basis of
   estimate, cross-references. A deck has none of those, so the control would
   pass or block on the wrong things. A second copy would also drift from the
   statement-of-work original.
2. Give build-deck a scope check of its own. Chosen. It asks the one question a
   deck needs answered: is each scope statement on a slide in the named
   statement of work or scope baseline, with the same in or out?

### The check

```
python3 scripts/check_scope_claims.py deck.pptx --source sow.docx --json scope-claims.json
```

The deck can be the `.pptx`, the `extract_pptx.py` HTML or JSON, or text. The
source can be `.docx`, `.pptx`, `.html`, `.md`, `.txt` or `.json`. Exit 0 means
every scope claim is supported. Exit 1 means a claim is unsupported (absent from
the source) or contradicted (in the source with the opposite in or out). Exit 2
means an unreadable input or a source with no scope statements. The JSON report
names the control `check-deck-scope-claims` and binds the deck and the source by
hash. The script header says what counts as a claim and where the check is
lexical.

### Recording it

In the quality record, run the check as the control `check-deck-scope-claims`,
cite the report path, and back each scope assertion with it:

```json
{"control": "check-deck-scope-claims", "verdict": "pass", "citation": "scope-claims.json"}
{"kind": "contract_scope", "text": "Delivery of wedding cakes is out of scope.",
 "supported_by": "check-deck-scope-claims"}
```

`quality_gate.py` accepts `review-contract-scope` or `check-deck-scope-claims`
as the control behind a `contract_scope` assertion, and as the control that
satisfies `artifact.contract_scope`. No other control can back a scope claim.

The check proves the deck repeats its source. It does not prove the source is
signed or current. A reviewer still reads the deck against it. With no named
source, the scope assertion stays `blocked`.
