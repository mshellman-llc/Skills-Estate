# Excel Workbook Format and Styling

The deliverable is a single `.xlsx` workbook with **two tabs**. This reference
covers the columns for each tab, the default visual theme, the Epics-tab
formula, and recalculation.

## Tab 1: "Epics" (Summary Tab)

| # | Column | Description |
|---|---|---|
| 1 | `Epic Name` | Name of the epic. |
| 2 | `Prefix` | The short prefix used in requirement numbering (e.g., `CPE`). |
| 3 | `Capability` | The broad business capability this epic supports. |
| 4 | `Business Need` | The strategic problem/opportunity driving this epic. |
| 5 | `Requirement Count` | **FORMULA**: `=COUNTIF(Requirements!C:C, A2)`. Counts how many requirements reference this epic. Must be a live Excel formula, never a hardcoded number. |

## Tab 2: "Requirements" (Detail Tab)

| # | Column | Description | Default |
|---|---|---|---|
| 1 | `Requirement Number` | Auto-numbered with epic prefix (e.g., `CPE-001`). **Auto-generate the prefix, then confirm with the user during hierarchy review.** | (none) |
| 2 | `Name` | Short, descriptive requirement name. | (none) |
| 3 | `Epic` | Epic name. Must exactly match an entry in the Epics tab column A. | (none) |
| 4 | `Capability` | The broad business capability. | (none) |
| 5 | `As A` | Persona/role in the user story. | (none) |
| 6 | `I Want To` | Desire/action portion of the user story. | (none) |
| 7 | `So That` | Business justification at the individual requirement level. | (none) |
| 8 | `Acceptance Criteria` | Gherkin-formatted criteria. Multiple scenarios separated by blank lines. Use actual newlines within the cell (openpyxl: `\n` in the string). | (none) |
| 9 | `Priority` | MoSCoW priority. See Canonical Values in SKILL.md. | `Must Have` |
| 10 | `Status` | Lifecycle status. See Canonical Values in SKILL.md. | `Draft` |
| 11 | `Assumptions & Notes` | Additional context, assumptions, dependencies. | (none) |

**Note:** Business Need lives exclusively on the Epics tab. It is the
strategic "why" for the entire epic and does not need to be repeated
on individual requirement rows.

## Excel Styling: Default Blue/White Theme

Apply this theme unless an Estate brand guidelines skill provides
official brand colors.

### Color Palette

| Element | Color (Hex) | RGB |
|---|---|---|
| Header row background | `#1F4E79` | (31, 78, 121), dark navy blue |
| Header row font | `#FFFFFF` | (255, 255, 255), white |
| Alternating row A | `#FFFFFF` | white |
| Alternating row B | `#D6E4F0` | (214, 228, 240), light blue |
| Epic tab header background | `#1F4E79` | same navy blue |
| Tab color: Epics tab | `#1F4E79` | navy blue |
| Tab color: Requirements tab | `#5B9BD5` | (91, 155, 213), medium blue |

### Formatting Rules

- **Font**: Arial, 10pt for data rows, 11pt bold for headers.
- **Header row**: Bold white text on navy background. Freeze the header row
  (freeze panes at row 2).
- **Alternating row colors**: Apply to data rows for readability.
- **Column widths**: Auto-fit where possible. Key guidance:
  - `Requirement Number`: 18
  - `Name`: 30
  - `Epic` / `Capability`: 30
  - `Business Need`: 40
  - `As A`: 25
  - `I Want To`: 45
  - `So That`: 40
  - `Acceptance Criteria`: 60
  - `Priority` / `Status`: 15
  - `Assumptions & Notes`: 40
- **Text wrapping**: Enable on `Acceptance Criteria`, `Business Need`,
  `I Want To`, `So That`, and `Assumptions & Notes` columns.
- **Acceptance Criteria cells**: Use actual newlines (`\n`) so Gherkin
  scenarios display on multiple lines within the cell. Set vertical
  alignment to "top".
- **Data validation** (optional but recommended):
  - `Priority` column: dropdown list to Must Have, Should Have, Could Have, Won't Have
  - `Status` column: dropdown list to Draft, Reviewed, Approved
- **Auto-filter**: Enable on the header row of both tabs.

### Epics Tab Formula

The `Requirement Count` column must use a live COUNTIF formula:

```
=COUNTIF(Requirements!C:C, A2)
```

Where `A2` references the epic name in that row and `Requirements!C:C` is
the Epic column on the Requirements tab.

### Recalculation

After generating the workbook, **always run recalculation** using the xlsx
skill's `scripts/recalc.py` (locate it via the xlsx skill's directory):

```bash
python <xlsx-skill-path>/scripts/recalc.py output.xlsx
```

Check the output for errors and fix any before presenting to the user.
