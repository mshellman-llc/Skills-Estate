---
name: interactive-proposal
description: 'Builds a single-file interactive proposal page that a prospect can click through. The page lets a prospect switch among scoped versions. Each version carries its team, timeline, assumptions, boundaries, and call to action. Proposal mode renders a priced scoping-app quote (Q-number) with every number tied to a quote field and reconciled by tie-out. Explorer mode covers pre-quote qualification with the same page and gates, scope and open decisions only, and zero currency on the surface. Use when asked for an interactive proposal, proposal page, quote page, clickable proposal, web version of the DDOC, scope explorer, or option explorer for a pursuit. Trigger on a Q-number or client name paired with interactive, page, site, explorer, or clickable. Do NOT use for the PPTX Deal Decision deck itself (that is ddoc) or a generic slide proposal deck (deck-builder).'
---


# Interactive Proposal

> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [`sow-proposal.md`](../prose-pass/references/registers/sow-proposal.md). Inputs, not a final pass.**

Turn a pursuit into a single-file interactive HTML page the prospect can explore: switch between
versions and watch the page re-render, read what each version includes, see what it defers, and
know what happens next. One file, no build step, opens from an email attachment.

## Pick the mode first, and say which one you are in

| Signal | Mode | What the switcher animates |
|---|---|---|
| A priced quote exists in the scoping app, or the user hands you an export | **Proposal** | Version totals, verbatim from the quote |
| Real client, no quote yet, or a quote that is unpriced or known stale | **Explorer** | A count computed from the source documents |

Without a quote, Explorer renders no currency. It uses source-backed boundaries and unresolved
choices so qualification work can proceed.

Announce the mode in your first line back to the user. It sets their expectations about numbers.

## Proposal mode

1. **Get the quote.** Scoping MCP first (`scoping_get_quote`, `scoping_get_sow_data`), then an
   export the user provides. That is the list. If neither exists, you are in Explorer mode.
2. **Assemble `proposal.json`** per `references/quote-contract.md`. One entry per scope version in
   the quote. Every displayed number maps to a named quote field.
3. **Write the parity manifest** at the same time, not after. See `references/release-gates.md`.
   Writing it before the HTML forces you to decide what must survive the render, which changes
   what you build.
4. **Build** per `references/patterns.md`.
5. **Pricing UX:** prospects switch between fixed versions. Totals are quote values. Tweening
   between two quote values is fine; arithmetic on the page is not. No toggleable line items, no
   financing, no "starting from" framing.
6. **Gate it** per `references/release-gates.md`, including figure tie-out against the quote.

## Explorer mode

Same page, same brand, same gates. The differences:

- **No currency anywhere.** Make it mechanical: put `$` in the manifest's `forbiddenPhrases`. A
  page that cannot leak a price cannot be quoted against you later.
- **The metric slot needs a real number.** Use something computable and checkable from the source
  documents: requirements covered, decisions open, interfaces in scope. State the counting method
  in the sources disclosure so the client can verify it against their own document.
- **Versions come from the client's own open decisions**, never from a good/better/best split you
  invented and never from internal estimate confidence bands. A low, expected, and high ROM range
  is an estimating artifact and does not become client-facing versions.
- **Say on the page why there is no price**, in one short block near the top. A stated reason
  reads as discipline; an unexplained absence reads as evasion.
- **Team and duration are absent too**, for the same reason, and the page says so.
- **Route to the paid next step** that produces the quote, and name its outputs.

## Build rules, both modes

**Brand.** Use the selected project profile or the neutral estate profile. Pass `--profile` to the builder when the user names a different profile. The shared runtime embeds declared local fonts and the optional logo; missing declared assets fail the build. No company assets are required.

**Self-contained output.** The delivered HTML embeds its data, styles, script and selected assets. It needs no server or external network resource. The source builder needs Python; browser checks additionally need Node.js, Playwright and Chromium.

**Structure.** Keep the `<main>` landmark in the skeleton. The parity gate requires it.

**Timeline.** In Proposal mode the builder draws each version's quoted phases with the timeline from `roadmap-artifacts`, on a Week 1, Week 2 axis, and redraws it when the version changes. The phase list stays as the fallback when a phase's `weeks` value is not `N` or `N-M`. The components are inlined, take their colors from the selected profile, and add no network request.

**Voice.** Apply the confirmed author profile and `prose-pass` while writing, not as a pass afterwards. The test for
every sentence is whether it carries a specific: a number, a named system, a named owner, or a
consequence. Scrubbing buzzwords without adding specifics fails the standard that matters even
when it passes the checker that runs.

**Honest copy.** Label every estimate. Put the validity or status line in the header and the
confidentiality line in the footer. Every not-included item carries a route, because a boundary
the client can see is a next conversation and a boundary they discover is a dispute.

**Print.** An `@media print` block so the selected version prints clean. Excluded scope cards drop
out of print; disclosures print open.

## Working builder and checks

Build a sourced page with the packaged entrypoint:

```bash
python3 scripts/build_proposal.py proposal.json --quote quote-export.json --output attempt-001/proposal.html
python3 scripts/build_proposal.py explorer.json --output attempt-001/explorer.html
python3 scripts/qa_proposal.py attempt-001/proposal.html
```

Add `--profile /path/to/brand.md` for an explicit confirmed profile. Existing outputs are refused. The build checks source IDs, excluded-item routes, option uniqueness, exact quote parity, and explorer counts. Browser QA exercises every version, disclosure, keyboard tab control, mobile width, and print output; it saves all screenshots and PDFs. Inspect those outputs and compare their meaning with the source before delivery.

The working schema is illustrated in `fixtures/explorer.json`, `fixtures/proposal.json`, and `fixtures/quote.json`. Each source has an ID, title, reference and revision. Each scope item has a stable ID and source ID. Explorer counts equal the number of distinct included item IDs; other counting methods require an explicit adapter and test before use. Proposal exports use the same version fields as the page. Map another quoting system into that contract while preserving its revision and original export.

Set `ESTATE_NODE`, `ESTATE_NODE_MODULES`, or `PW_CHROMIUM` when those runtimes are outside the normal project paths. Browser QA launches an isolated profile and blocks remote resource requests. A builder receipt proves generation only; passing browser checks and a source review establish usability for the tested input.

## Release gates

Read `references/release-gates.md` and run all three. The page is not deliverable until parity,
visual, and prose each have a written disposition. Do not narrate the gate runs; report the result
and the dispositions you made.

## What this skill does not do

- **Pricing.** The scoping app owns the number. This skill renders it and never computes it.
- **Scope language.** The scoping process authors it. Tighten grammar here, never meaning.
- **Client-facing invention.** Every figure and claim traces to a quote, source document, or named system of record. The bundled fictional fixtures are labeled tests and never substitute for client evidence.

## References

- `references/release-gates.md` - the three gates, exact commands, manifest schema, visual QA.
- `references/quote-contract.md` - proposal.json shape, field mapping, audit trail, both modes.
- `references/patterns.md` - page skeleton, version switcher, tweened counts, disclosures.
- `references/synthetic-scope-explorer.manifest.json` - a synthetic explorer manifest for regression checks.

## Release gate (required)

Run the gate before delivery. A reviewer receives the completed result and its evidence. Full spec in
[`release-gate.md`](../_shared/release-gate.md).

1. Apply writing-integrity to the prose. Use the bundled diagnostic tools to check saved writing. For
   a final artifact it emits a receipt the quality gate requires.
2. Run brand-renderer on the branded artifact: palette, borders, radii, logo,
   footer.
3. Run quality-gate before you call it final.

Do not present the artifact as finished until every check that applies has passed.
