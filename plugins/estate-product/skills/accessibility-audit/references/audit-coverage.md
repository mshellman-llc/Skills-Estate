# Audit coverage

## Set the boundary

Use [WCAG 2.2](https://www.w3.org/TR/WCAG22/) as the default standard. Record the requested interface, sampled states, browser, assistive technology when used, and source version or observation date. Include complete paths such as login and form submission when they are in scope. An isolated component review leaves its surrounding process untested.

## Select checks for the interface

Automated checks can expose some markup problems and contrast failures. They can also flag missing accessible names. Preserve the tool's output and investigate it in context. An empty issue list covers only that tool's checks in that state.

Choose manual checks that apply to the interface:

- Test keyboard access and traps, then follow the focus sequence. Check whether focus is visible and whether author-created content hides it.
- Inspect headings and landmarks for structure and navigation.
- Check control names and state changes through interaction.
- Inspect meaningful images and media alternatives for equivalent information.
- Test error handling and instructions in the relevant form states.
- Inspect zoom and reflow behavior. Measure applicable color and contrast requirements.
- Test motion controls and touch or pointer operation where present.

Use the criterion's conditions and exceptions for each check. Do not impose a single screenshot width or one contrast threshold on all content.

Record screen-reader and browser combinations actually used. Check announced names, roles, states, and changes through the interaction. DOM inspection can suggest an announcement issue but does not establish what a screen reader said. If screen-reader testing is unavailable, mark it untested and identify the journey needing that check.

## Include the WCAG 2.2 additions

The new A and AA criteria are:

| Criterion | Review question |
| --- | --- |
| [2.4.11 Focus Not Obscured (Minimum), AA](https://www.w3.org/TR/WCAG22/#focus-not-obscured-minimum) | Is a focused component entirely hidden by author-created content? |
| [2.5.7 Dragging Movements, AA](https://www.w3.org/TR/WCAG22/#dragging-movements) | Is a single-pointer alternative available without dragging, subject to the criterion's exceptions? |
| [2.5.8 Target Size (Minimum), AA](https://www.w3.org/TR/WCAG22/#target-size-minimum) | Does each target meet the 24 by 24 CSS pixel requirement or an applicable spacing or other exception? |
| [3.2.6 Consistent Help, A](https://www.w3.org/TR/WCAG22/#consistent-help) | Do repeated help mechanisms occur in the same relative order under the criterion's conditions? |
| [3.3.7 Redundant Entry, A](https://www.w3.org/TR/WCAG22/#redundant-entry) | Can previously supplied information be reused in the same process, except where the criterion allows re-entry? |
| [3.3.8 Accessible Authentication (Minimum), AA](https://www.w3.org/TR/WCAG22/#accessible-authentication-minimum) | Does authentication avoid a cognitive function test or provide one of the permitted alternatives or mechanisms? |

These questions guide inspection; they do not replace the normative text. [W3C's overview of the additions](https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/) explains their purpose. Focus Appearance 2.4.13, Focus Not Obscured (Enhanced) 2.4.12, and Accessible Authentication (Enhanced) 3.3.9 are AAA. Parsing 4.1.1 was removed from WCAG 2.2; use the requested version when reviewing older targets.

## Report a finding and its coverage

Explain the barrier and the affected user task. Record the environment and reproduction, with an exact evidence location. Cite the relevant criterion. Propose a correction and describe the verification it needs. Retain a concise coverage record of each check and its outcome; a pass is specific to the tested state. Mark untested areas explicitly. Separate a plausible issue awaiting interaction from an observed failure. State whether a retest examined local code, a preview, or the live destination.
