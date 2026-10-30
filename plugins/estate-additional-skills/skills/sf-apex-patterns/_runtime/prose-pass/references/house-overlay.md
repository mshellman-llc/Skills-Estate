# Project writing requirements

The estate writing standard applies before drafting and throughout revision. Project requirements can add terminology and confirmed voice guidance. They cannot exempt internal records or disable construction checks.

## Adding restrictions

The bundled `house.json` supplies the baseline. A separate configuration can add `banned_terms`, `banned_chars`, and `hedge_openers`. The checker combines those lists with the baseline. Empty lists do not remove existing rules.

```json
{"banned_terms": ["next-generation"]}
```

```bash
python3 scripts/writing_check.py --config project-writing.json DRAFT.md
```

Configuration overrides cannot change budgets, disable rules, or add repetition exemptions. Revise the text when the checker finds a problem. Preserve an exact required source span with its source recorded; review all new language around it.

## Applying the standard

Load the writing standard before producing text. Reference it from the host instructions that govern the task. Each canonical estate package includes the policy and writing runtimes.

Check the files that contain authored language. Include instructions and internal records. Report unsupported inputs and read their extracted text explicitly. A successful scan still requires reading the finished result for meaning and recurring sentence patterns.

The checker's FAIL and WARN labels describe confidence. Both require attention before completion. A diagnostic density score is not a release decision.
