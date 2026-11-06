# Review rules

These rules come from reviewer comments on earlier review sites. Each one names the check that enforces it. `browser` rules run in `checks/browser_checks.cjs`, `data` and `writing` rules run in `lib/rsk/gate.py`, and `reading` rules need a person or agent to read the rendered page.

When a reviewer's comment changes how a page should look or read, add a dated row here in the same turn as the fix. Add or extend the check when a computed style or the data can test the rule. A rule recorded here applies to every later engagement, not only the page where the comment landed.

| ID | Rule | Check | Added |
|---|---|---|---|
| R-TYPE-1 | A table uses one text size for headers, cells, links and statuses. Ticket lists inside a table row sit behind a closed line. | browser | 2026-11-04 |
| R-FOLD-1 | Next actions, unclassed tickets, sources and technical design start closed. They open on click or from a link to them. | browser | 2026-11-04 |
| R-DEC-1 | A closed decision card shows the question and its status only. Owner and answer appear after the card opens. The status button sits beside the card's summary, not inside it, so it stays a separate keyboard stop. | browser | 2026-11-04 |
| R-DEC-2 | A question's status can be changed on the page and saves to the shared store. A saved answer marked Answered or Proposal accepted sets the status to Answered. No second "answered" flag sits next to the status. | reading | 2026-11-04 |
| R-COLOR-1 | Body text and headings use the text color. The accent fills the nav bar, links, buttons, selected states, class chips and status tags only. | browser | 2026-11-04 |
| R-TINT-1 | Process steps are tinted tiles that get one shade darker per step. The selected step is solid accent. | browser | 2026-11-04 |
| R-NUM-1 | Step number circles are one fixed size on every page. | browser | 2026-11-03 |
| R-STATUS-1 | Every ticket status on the page matches the latest tracker export. | data (D3) | 2026-11-04 |
| R-STATUS-2 | A status color always appears with its text label. | reading | 2026-11-04 |
| R-LAYOUT-1 | No page scrolls sideways at 390 px. Wide diagrams scroll inside their own box. | browser | 2026-11-04 |
| R-ERR-1 | No page throws a script error. | browser | 2026-11-04 |
| R-COUNT-1 | No paragraph of counts or percentages sits above or inside the story map. Readiness rules live in the Readiness filter's tooltip. | reading | 2026-11-04 |
| R-SECT-1 | A section stays only when it helps someone classify, decide or build. Sections that list work outside the release, repeat another page, or explain the page itself are removed. | reading | 2026-11-04 |
| R-ID-1 | Ticket keys and internal IDs appear in the critical path and in the tracker link targets, not in titles or running text. | reading | 2026-11-03 |
| R-LABEL-1 | Filter and tab labels use the client's own role and team names, without added qualifiers. | reading | 2026-11-03 |
| W1 | Every authored string passes the estate writing checker. FAIL findings block publishing; WARN findings get a reading pass. Tracker text and recorded client answers are source text and are not rewritten. | writing | 2026-11-04 |
| D1 | Every referenced story, question, group, step, role and ticket exists. Ids are unique and use only letters, digits and `_ . ~ : @ + -`. No two stories share a primary ticket. Blocks cycles are reported. | data | 2026-11-04 |
| D2 | The whole rendered data file equals a fresh computation from the sources. | data | 2026-11-04 |
| D3 | Each story's status equals its primary ticket's tracker status. | data | 2026-11-04 |
