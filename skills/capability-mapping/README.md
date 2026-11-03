# Capability mapping

Build one business capability map, place it on the customer lifecycle and the strategy, score current and target maturity with business impact, and rank the gaps to close.

Start with [SKILL.md](SKILL.md), then read [the method](references/method.md). The [model schema](references/model-schema.md) defines the JSON source, the [workshop kit](references/workshop-kit.md) runs the lifecycle session, and [rendered outputs](references/rendered-outputs.md) describes the HTML, workbook and readout. [The synthetic fixture](fixtures/synthetic-model.json) is a complete example model.

`scripts/build_capability_map.py` validates the model, computes gaps and bands, and writes every output. The workbook and workshop commands need `openpyxl`. Shared writing and branding rules are added by the estate build. Governed client maps also use `evidence-core`; shared project records go through `knowledge-hub`.

The method generalizes a capability-mapping course draft by Divya Alavarthi (created 2024-08-11) that was supplied as source material. The skill paraphrases its method and examples; it does not reproduce the course text, its images or any vendor capability catalog. The course scores current execution in red, yellow or green, with high, medium or low business impact. The 0 to 5 maturity scale, the target score, the gap-times-impact ranking and the priority bands are this skill's additions.
