# Scoping Methodology

Deep methodology for the scoping-agent skill: writing scope descriptions and
assumptions, estimating hours, the dual pricing model, and timeline staffing rules.
SKILL.md carries the high-level workflow and points here.

## Writing scope descriptions and assumptions

**Structure:** a description is a 1-3 sentence header, rarely longer, with most of
the content in bullet points. Assumptions are bullet points too.

**Bullets are active-voiced and verb-led.** Each bullet says what the team will do,
not a noun fragment:

- Bad: "Future-state process documentation across marketing and sales"
- Good: "Create future-state process documentation across marketing and sales"
- Bad: "Lead lifecycle definitions: statuses, MQL threshold handoff, disqualification
  and recycle paths"
- Good: "Facilitate defining the lead lifecycle, including statuses, MQL threshold
  handoff, and disqualification and recycle paths"
- Bad: "MQL and lead conversion visibility"
- Good: "Ensure MQL and lead conversion information is visible in reporting"

**Cut the filler:**

- No em-dashes anywhere in descriptions or assumptions.
- No conversational sequencing language unless it is scope-relevant. "Current state
  analysis of the lead and MQL flow across systems" ends there; "before rebuilding
  it" adds nothing.
- No business goals in scope items. The SOW executive summary carries goals; scope
  items carry technical scope. Cut lines like "Core engagement goal: OOTB-first
  usage after five years of unsupported drift."
- No useless qualifiers. "Replace manual month-end pulls with reports and dashboards"
  is complete; "that give day-to-day value" is filler.

**Cross-references use full scope item names.** When one item points at another
(disambiguation is the common case), name it in full: "Duplicate matching rules are
covered in Data Quality & Deduplication Rules." Never a pseudo-abbreviation like
"covered in DQ&DR"; the meta pointer becomes confusing.

**Assumptions commit to a state.** An assumption is an assumption, not an open
question. "Prior agency documentation may or may not exist; client investigating"
is bad. Pick the state that bounds the work and assert it: "No prior agency
documentation is available." The client corrects it in review if wrong.

## Estimating hours

Don't proactively estimate during scope definition; offer it once items are pushed.
When estimating:

1. **Calibrate with capability stats** from `scoping_get_skills`: median/IQR of
   historical hours per capability. Simple maps to Q1, typical to median, complex to
   Q3. Check `pricingStatsConfidence` (high is 10+ items, medium is 5+, low means
   judgment only). Stats can be sparse for less-common capabilities; when confidence
   is low, lean on anchor-based estimation or experience instead.
2. **Decompose with leverage ratios** from the team preset: senior hours seed each
   phase, juniors derived per-phase (R&D ~1.5x, Build ~3x, Validate ~2x, Train ~1x),
   indirect roles (PM/CSE) as a percentage of direct labor.
3. **Anchor-based alternative:** if the user says "2 weeks of DEV build", that's 80h
   DEV build. Back out the other phases from the phase split (standard 30/40/20/10),
   then apply leverage for other roles.
4. Push via `upsert_resources` (phase fields: `requirementsDesignHours`, `buildHours`,
   `validateHours`, `trainDeployHours`). Do the math silently; present the final
   matrix and a one-line method summary, then push and link.

Validate staffing sanity against product config (`scoping_get_quote` with
`include: ["products"]`): each role has `minHoursPerWeek` and `hoursPerWeekInterval`.
DEV-type roles are usually 40h/wk; SA/TA 10 to 20; PM 10 to 20.

## Dual Pricing Model: Bottoms-Up vs Timeline

Two intentionally decoupled views of the same project:

- **Bottoms-up (BU)** is analytical: scope items with role-hour allocations. Proves
  you understood the work. Managed via `upsert_resources`.
- **Timeline** is a staffing experiment: FTE instances staffed across weeks. **Drives
  the actual quote financials.** Managed via timeline snapshots.

There is no per-item mapping between them; resources may appear on one and not the
other. The timeline exists for margin experimentation (swap title levels, restaff,
compare snapshots). BU validates the timeline via `phaseComparison`; they should land
in the same neighborhood (thresholds: timeline under BU by 5% = warning, 15% = error;
over by 20% = warning, 35% = error, since under-scoping is the bigger risk). When
discussing scope items talk role hours; when discussing timelines talk FTEs and weeks.
Never map item hours to specific weeks.

**Role vs Title Level:** Role (Product2) drives bill rate; Title Level drives cost
rate. Upstaffing means lower margin and lower risk; downstaffing is the reverse.

## Timeline Staffing Rules (when hand-tuning)

- **Longest pole:** the resource with the most hours sets duration (hours ÷ 40, round up).
- **Continuity:** once staffed, a resource works every week until rolloff, no gaps.
  Ramp up/down is fine.
- **Oversight pairs (enforced):** DEV requires TA/STA on the timeline (ERROR); BA
  requires SA/SSA (ERROR); SD and SBA same pairs as WARNING. Consolidate small roles
  upward (give a thin DEV scope to the SD) to avoid oversight problems entirely.
- **"You build it, you test it":** resources stay through Validate by default.
- **Staffing increments:** respect each role's `minHoursPerWeek` / `hoursPerWeekInterval`;
  the validation engine flags violations per cell.
