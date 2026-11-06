---
name: build-moscow-story-map
description: Build and maintain a MoSCoW story map from tracker tickets. Places stories by workflow step and class, computes readiness and Must share, lists unclassed tickets, draws the critical path from Blocks links, and queues changed or new tickets for mapping. Use for "class the release stories by workflow step", "what is ready to build", "what's on the critical path", or mapping new tickets after an export. Do NOT use for MoSCoW values on captured requirements in the requirements workbook (capture-requirements), INVEST grading and sprint readiness reports (refine-backlog), ranking by value (prioritization), or writing new stories (capture-requirements).
---

# Build moscow story map

The story map is `content/stories.json`: steps down the side, classes across, one entry per story. You write the judgment fields. The script computes everything that comes from the tracker, so statuses and estimates never drift from the export.

## Write the stories

Read the release's epics and tickets in `tracker/tickets.json` and the client's workflow steps. For each story, record these fields:

- `id`, `label`, `step` and `class`: `must`, `should`, `could` or `wont`.
- `tickets`: the primary ticket first.
- `roles`, plus `what` (what it does, in one sentence) and `interim` (the manual workaround until it is built).
- `depends_on` for story-level dependencies.

A planned story with no ticket yet gets an empty `tickets` list and `planned_in` set to the epic that plans it.

Take class definitions from the client. Put them in `config/site.json` under `classes`, and never write your own. A class is the client's decision. A proposed class change goes through the story panel's class review or the decision register, not a silent edit.

Do not store status, sprint, points or readiness in `stories.json`; the renderer computes them. Leave acceptance criteria to the tickets unless the client wrote them somewhere else; then list them under `acceptance`.

## Calculate

```bash
python3 scripts/story_map.py summary --config <project>/config/site.json \
  --content <project>/content --tickets <project>/tracker/tickets.json
```

The summary reports these values:

- Stories by class and the stories that are not ready.
- Open points per class and the Must share.
- Unclassed tickets: open tickets under the release epics that no story references.
- The critical path: open Must tickets, their open upstream blockers, and Musts not in the tracker yet.

A story is ready when it meets every rule in `config.readiness`. The default rules are acceptance criteria, an estimate, no open question and no blocked or unticketed dependency. A done story is always ready.

## After a new export

```bash
python3 scripts/story_map.py queue --content <project>/content \
  --tickets <project>/tracker/tickets.json --delta <project>/tracker/delta.json --out <project>/tracker
```

`review-queue.md` lists two groups:

- Stories whose tickets changed, with each field change.
- New tickets, each with candidate stories ranked by shared words and epic.

Decide each new ticket: add it to a story's `tickets`, create a story with a class the client gave, or leave it in Not yet classed. Revise a story's `what` or `interim` only when its ticket's change makes the text wrong. Leave unaffected stories as they are.

## Export class reviews

The published Scope page saves class decisions to the shared store (`moscow/<story id>`). Read them with the artifact data tool, save them as JSON, and export:

```bash
python3 scripts/story_map.py export-reviews --config <project>/config/site.json --content <project>/content \
  --tickets <project>/tracker/tickets.json --reviews moscow.json --out <project>/exports
```

`class-reviews.csv` lists each story, its ticket, the class on the map, the class decided and the reviewer's note, ready to import into the tracker.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
