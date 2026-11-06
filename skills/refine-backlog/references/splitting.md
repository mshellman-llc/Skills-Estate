# Splitting requirements

Split a requirement when it fails Small or Estimable, or when it carries several user outcomes in one row. Every slice must still pass INVEST on its own and must deliver something a user can see.

## Vertical, not horizontal

A horizontal split cuts by layer: schema, then service, then interface, then cache. The first slice has no user value, the rest depend on it, and nothing can be shown until the last layer lands. If priorities change halfway, nothing has shipped.

A vertical split cuts by user outcome and crosses every layer. For "build the admin dashboard":

1. The admin sees the account name and current plan.
2. The admin sees the last five activity events.
3. The admin sees usage against the plan limit.
4. The admin changes plan from the dashboard.

Each slice can be demonstrated, fits in a few days, and lets the team learn from slice 1 before building slice 4.

## Choosing a pattern

Walk the questions in order and use the first pattern that applies. When several apply, choose the one whose first slice is smallest and still useful.

| Question | Pattern | Recipe | Example |
|---|---|---|---|
| Can the team plan it at all? If not: | Spike | Timebox an investigation of two to three days with one owner and a written question ("we will know whether one SAML library supports all three identity providers"). The spike produces a decision, not a feature; re-split afterwards. | Spike on SAML against three providers, then one slice per provider |
| Does it span several workflow steps? | Workflow steps | One slice per step, in the order a user meets them | Checkout becomes add to cart, enter payment, confirm order, send receipt |
| Does it embed several business rules? | Business rule variations | One slice per rule | Discounts become loyalty tier, promo code, volume pricing |
| Does it include error handling? | Happy and unhappy paths | Ship the valid path first, then each failure path | Submit a valid application; then validation errors; then service failures |
| Does it support several inputs, outputs or platforms? | Interface variations | One slice per channel or format, when user behaviour differs | Search by keyword, by category filter, by voice |
| Does it handle several data types or sources? | Data variations | One slice per type | Export as CSV, then PDF, then XLSX |
| Can the same data be entered several ways? | Data entry methods | One slice per method | Add a contact by form, by paste, by file upload, by sync |
| Is performance or scale the hard part? | Defer performance | Ship a working version, then a slice for the performance target | Search at current speed; then search under 200 ms at the 95th percentile |
| Does it imply several operations on one record? | Operations | Read, then create, then delete, then update | Saved searches: view, create, delete, edit |
| Is the effort mostly one-time setup? | Major effort first | The first instance carries the setup; later instances are small | Salesforce integration builds the framework; HubSpot and Pipedrive reuse it |
| Do the acceptance scenarios describe separate outcomes? | Test scenarios | One slice per scenario group | Sign in with password; with SSO; with MFA |

If no question applies, the requirement is probably small already; ask the team to re-estimate.

Mike Cohn's SPIDR groups the same moves into five buckets: spikes, paths (workflow and happy or unhappy paths), interfaces, data, and rules. Use whichever names the team remembers.

The two upstream sources this reference merges list the "nine" patterns differently: one includes test scenarios, the other data entry methods and an optional major-effort pattern. All of them are kept here.

## Worked splits

**Enterprise sign-on, estimated at 15 days.** Split by scenario: SSO with the first identity provider, IdP-initiated only (4 days); the second provider, reusing that work (2); sign-in started from our own domain (3); creating users on first sign-in (3); the admin setup screen (3). Slice 1 alone gives enterprise customers a working sign-in.

**Notifications, estimated at more than 20 days and too vague to estimate.** Split by channel and rule: in-app banner for billing failures (3); in-app notice of new comments (2); email for billing failures (2); daily email digest (4); notification preferences (3); mobile push (5), deferred until in-app use shows demand.

## Recording a split

Splits change the requirements record, so they follow capture-requirements's rules:

- Each slice gets a new Requirement Number in the same epic. The original row keeps a canonical Status value; its Assumptions & Notes cell records "Split into" with the new numbers, and each new row names its parent in the same column.
- Each slice gets its own user story and at least one complete Gherkin scenario. Split the original scenarios between slices; do not copy them all to every slice.
- A slice inherits the original row's Source column value (see capture-requirements's traceability reference).
- The client or Product Owner confirms the MoSCoW priority of each slice; the split itself does not set it.

## Mistakes to avoid

| Mistake | Result | Fix |
|---|---|---|
| Splitting by layer or team | No slice can ship alone | Every slice crosses all layers |
| A first slice that holds everything difficult | One huge slice and several trivial ones | Make slice 1 the smallest end-to-end outcome |
| A spike without a written question | The spike never ends | State what the team will know when it ends |
| Splitting by platform when users behave the same everywhere | Duplicate slices with no added value | Split by user outcome first |
| The same pattern every time | Better splits are missed | Try a second pattern and compare first slices |
| Slices with no user payoff | They fail Valuable | Write the So That statement for each slice |
| Splitting live in the refinement session | Sessions run past 90 minutes | Pre-split the largest items; use the session to check them |

After splitting, grade every new row with `readiness_check.py`. Small also means the slice fits under the team's 85th-percentile cycle time when that measure exists.
