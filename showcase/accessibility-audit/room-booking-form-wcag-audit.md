---
skill: accessibility-audit
title: WCAG 2.2 AA audit of a library room booking form
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 30aae4a806f649376a0039a123b775be7e337a18041f3f55bae04bd41fd6d3ce
---

## Request

Can you audit our room booking page against WCAG 2.2 AA before the library launch next week? I've pasted the form markup and my own notes from a quick test session in the inputs folder. I need a list of what to fix first.

## Inputs

Run of the built `accessibility-audit` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### booking-form.html

<!-- Room booking page, staging build 2026-11-02 -->
<header class="site-header" style="position:sticky;top:0;height:120px">
  <a href="/"><img src="logo.png"></a>
  <nav>...</nav>
</header>
<main>
  <div class="page-title">Book a study room</div>
  <form id="booking" action="/book" method="post">
    <div class="field">
      <span>Full name</span>
      <input type="text" name="name">
    </div>
    <div class="field">
      <label for="email">Email</label>
      <input type="text" id="email" name="email" placeholder="you@example.com">
    </div>
    <div class="field">
      <label for="date">Date</label>
      <input type="date" id="date" name="date" required>
    </div>
    <div class="field">
      <label>Room size</label>
      <div class="radio" onclick="pick('small')"></div> Small (2-4)
      <div class="radio" onclick="pick('large')"></div> Large (5-8)
    </div>
    <div class="field">
      <label for="card">Library card number</label>
      <input type="text" id="card" name="card" autocomplete="off" onpaste="return false">
    </div>
    <div id="error" style="color:#e57373"></div>
    <button type="submit" class="btn" style="width:20px;height:20px">&#10003;</button>
  </form>
</main>
<style>
  :focus { outline: none; }
  .field input { border: 1px solid #ccc; }
</style>

#### test-notes.txt

Test notes, Priya Anand, 3 Nov 2026
Environment: Chrome 130 on macOS, staging site. Keyboard only, then 200% browser zoom. No screen reader, no axe or Lighthouse run.

- Tabbing from the top: can't see where focus is on any field. Had to guess.
- Tab reaches name, email, date, card, then the tick button. Room size options were skipped completely; Space/Enter did nothing on them.
- At 200% zoom the sticky header takes about a third of the screen. When I tabbed down to the card field it scrolled under the header and I lost it until I scrolled up manually.
- Submitted with the card field empty: the page reloaded, a pale red message appeared at the bottom ("Please check your entries"). Didn't say which field.
- Tried pasting my card number from my password manager: blocked.
- The submit button is a small tick, I missed it with my mouse twice.
- Help chat link is bottom-left on the booking page and bottom-right on the account page.
- Did not test: the confirmation page, the account pages, mobile, the date picker popup beyond opening it.

## Output

### Room booking page: WCAG 2.2 AA audit

The booking form is not ready to launch. A keyboard user cannot choose a room size, so the booking cannot be completed by keyboard. Fix the six blockers below first. Everything here covers the booking form only, in the state and environment listed under Scope. It does not show that the page conforms or fails as a whole.

#### Scope and method

- **Target:** WCAG 2.2, level AA (A and AA criteria, including the six added in 2.2).
- **Sampled:** the staging booking form (build dated 2 Nov 2026), initial state and the empty-card-number error state.
- **Evidence used:**
  - Priya Anand's manual session on 3 Nov: Chrome 130 on macOS, keyboard only, then 200% zoom.
  - The pasted markup, read as static code.
  - Two contrast ratios I calculated by hand from the CSS colors.
- **Not run:** no automated scanner, no screen reader, no mobile or touch testing. I have no browser here, so I did not reproduce anything myself. Findings marked "observed" rest on Priya's notes.
- **Contrast assumption:** the markup does not state the page background. I assumed white.

#### Fix before launch

| # | Barrier | Criterion | Status |
| --- | --- | --- | --- |
| 1 | Room size cannot be chosen by keyboard | 2.1.1 Keyboard (A), 4.1.2 Name, Role, Value (A) | Observed |
| 2 | Focus indicator removed | 2.4.7 Focus Visible (AA) | Observed |
| 3 | Sticky header hides the focused field at 200% zoom | 2.4.11 Focus Not Obscured (Minimum) (AA) | Observed |
| 4 | Error message names no field and has weak contrast | 3.3.1 Error Identification (A), 1.4.3 Contrast (Minimum) (AA) | Observed (3.3.1); calculated (1.4.3) |
| 5 | Pasting into the card number field is blocked | 3.3.8 Accessible Authentication (Minimum) (AA) | Observed; applicability needs a decision |
| 6 | Submit button is a 20 px tick with no text name | 2.5.8 Target Size (Minimum) (AA), 4.1.2 | Size from code; name suspected |

##### 1. Room size cannot be chosen by keyboard
- **Where:** the "Room size" field.
- **Steps:** Tab through the form. Focus moves from the card field to the tick button and skips the room size options. Space and Enter on them do nothing (Priya's notes).
- **Cause:** the options are empty `<div class="radio" onclick="pick(...)">` elements. They have no role, no tab stop and no key handler. The label text sits outside them, and the group's `<label>` has no `for` target.
- **Impact:** a keyboard or switch user cannot complete a booking. A screen-reader user would not be told that radio buttons exist, though I did not test that.
- **Fix:** use `<fieldset><legend>Room size</legend>` with two native `<input type="radio" name="size">` elements, each with its own `<label>`. Delete the click handler. Make the choice required.
- **Verify:** select each size with the arrow keys and Space, then submit.

##### 2. Focus indicator removed
- **Where:** the whole page. The stylesheet contains `:focus { outline: none; }`, and Priya could not see focus on any field.
- **Impact:** keyboard users cannot tell which control is active.
- **Fix:** delete the rule. Add a `:focus-visible` style with a 2 px outline offset from the control, with at least 3:1 contrast against the adjacent colors.
- **Verify:** Tab through every control in Chrome and in a second browser.

##### 3. Sticky header hides the focused field
- **Where:** the header is `position:sticky` and 120 px high. At 200% zoom it fills about a third of the viewport. Tabbing to the card field scrolled it behind the header (Priya's notes).
- **Criterion note:** 2.4.11 fails only if the component is entirely hidden. Priya lost the field, which suggests it was fully covered, but she did not record whether any part was visible. Confirm this when retesting.
- **Fix:** add `scroll-padding-top` at least equal to the header height on `html`, or let the header scroll away at zoomed sizes. Remove the fixed 120 px height.
- **Verify:** at 200% and 400% zoom, Tab to each field and the button and check that each is visible.

##### 4. Error message
- **Where:** the `#error` element. After submitting with the card number empty, the page reloaded and showed "Please check your entries" at the bottom, with no field named (Priya's notes).
- **Failures:**
  - 3.3.1: the message does not say which field is wrong or why.
  - 1.4.3: `#e57373` on white is about 3.0:1. Normal-size text needs 4.5:1.
- **Suspected, untested:** the markup has no `role="alert"` or live region, and the page reloads, so a screen reader may not announce the error. This needs a screen-reader test (3.3.1, 4.1.3 Status Messages).
- **Fix:**
  - Mark the card field `required` and `aria-describedby` an inline message such as "Enter your library card number."
  - Place a summary of links to the failing fields at the top of the page after submission, and move focus to it.
  - Use a text color of at least 4.5:1, for example `#b3261e`, and do not rely on color alone.

##### 5. Paste blocked on the card number
- **Where:** `<input id="card" onpaste="return false">`. Priya's paste from a password manager was blocked.
- **Criterion:** 3.3.8 requires that authentication not depend on transcribing or remembering something, and paste is a permitted mechanism. Whether this field counts as authentication depends on whether the card number is used to verify identity here. I treated it as likely applicable. The owner of the booking flow should confirm.
- **Fix:** remove `onpaste`. Remove `autocomplete="off"` as well, so password managers can fill the field.
- **Verify:** paste a 14-digit number and submit.

##### 6. Submit button
- **Where:** `<button class="btn" style="width:20px;height:20px">&#10003;</button>`.
- **Size:** 20 by 20 CSS px is below the 24 by 24 minimum in 2.5.8. The spacing exception could apply if no other target sits within 24 px, which I could not check without a render. Priya missed it twice with a mouse, which is the practical problem regardless.
- **Name (suspected):** the only content is a check mark glyph. Screen readers commonly announce a glyph like this as "check mark", not as the action. Needs a screen-reader test.
- **Fix:** use a visible text button, "Book room", with a target of at least 44 by 44 px.

#### Fix next

| Barrier | Criterion | Status |
| --- | --- | --- |
| "Full name" is a `<span>`, not a label, so the input has no accessible name | 1.3.1 Info and Relationships (A), 3.3.2 Labels or Instructions (A), 4.1.2 | Code only; naming not confirmed with assistive technology |
| Email is `type="text"`, and name and email lack `autocomplete` values (`name`, `email`) | 1.3.5 Identify Input Purpose (AA) | Code only |
| Only the date field is marked `required`; no visible required indicator or instructions | 3.3.2 | Code only |
| Input borders `#ccc` on white are about 1.6:1; the field boundary needs 3:1 | 1.4.11 Non-text Contrast (AA) | Calculated, assuming a white background |
| The logo `<img>` has no `alt`, so the home link has no name | 1.1.1 Non-text Content (A), 2.4.4 Link Purpose (A) | Code only |
| "Book a study room" is a `<div>`, so the page has no heading structure | 1.3.1, 2.4.6 Headings and Labels (AA) | Code only |
| Help chat sits bottom-left on this page and bottom-right on the account page | 3.2.6 Consistent Help (A) | Observed on two pages |

The 3.2.6 finding depends on the two pages sharing the help mechanism in a set of pages; Priya's note supports that. Fix by placing the link in the same position in the shared template.

#### Coverage record

| Area | Result |
| --- | --- |
| Keyboard operation and focus order | Failed (items 1, 2). The order of the controls that are reachable is logical. |
| Focus visibility and obscuring | Failed (items 2, 3) |
| Error handling, empty card number | Failed (item 4) |
| Zoom at 200% | Tested only for focus obscuring. Reflow at 320 CSS px width (1.4.10) not tested. |
| Dragging movements (2.5.7) | The markup has none. The date picker popup was opened but not operated, so untested. |
| Redundant entry (3.3.7) | The form is a single step, so nothing is asked twice here. The confirmation page was not tested. |
| Accessible authentication (3.3.8) | Failed if applicable (item 5) |
| Screen reader names, roles, states, announcements | **Untested.** Needs a pass on the booking journey: fields, room size group, error, submit. |
| Automated scan | **Not run.** |
| Mobile and touch | **Untested.** |
| Confirmation page, account pages | **Untested.** |
| Page language, title, landmarks | Not visible in the pasted fragment; check the full page. |

#### Next steps

1. Fix items 1 to 6, then retest with keyboard at 100%, 200% and 400% zoom.
2. Run NVDA with Firefox or VoiceOver with Safari on the full journey, from room size through the error state to the confirmation page. That covers the suspected issues in items 4 and 6.
3. Run axe or a similar scanner on the booking page and the confirmation page, and keep the output.
4. Decide whether the library card number counts as authentication (item 5).

A clean retest of these items would confirm the fixes in the tested browser. It would not make the site conformant or compliant by itself.

#### Files

No files were produced. This answer is the deliverable.
