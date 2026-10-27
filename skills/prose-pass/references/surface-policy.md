# Writing scope

The [estate writing standard](estate/writing.md) applies to all authored language. Read it before writing. A file's audience or format cannot exempt it.

Instructions and internal records follow the same writing rules as a final deliverable. This includes agent guidance, audit explanations, structured text fields, and comments in source code. Review short messages before returning them. Check saved text with `writing_check.py`, then read the finished result.

Preserve exact source evidence and required executable syntax. Protect only the exact spans that require preservation. New explanations around those spans remain subject to review. Formatting your own prose as a quote or code block does not exempt it.

For a substantive rewrite, retain the original and revised files. Check the required meaning against the source after editing. A consequential decision requires deeper factual review; it does not create a separate writing standard for routine work.

A missing tool or unsupported format requires a reading pass. Do not report a scanner pass for an unscanned artifact. Repair detected writing patterns rather than lowering the checker settings or relabeling the text.

The extractor reads JavaScript strings, template text, comments and embedded JSON without executing the script. Operators, variable names and regular-expression syntax are code. Text in UI attributes and event-handler strings remains under review. An incomplete string, template or comment returns an extraction error.

Structured values keep their boundaries for fragment checks. Two labels in different cells are not consecutive body sentences; stacked fragments inside either cell still fail. Repetition checks count an exact citation once when it is a feeling's `source` paired with an `observed` or `reported` basis, or an entry in `metadata.sourceLabels`. Every occurrence remains subject to the other writing checks. Dates keep their actual value and count as one token in repetition checks. Markdown table-column boundaries do not join unrelated fields into a repeated phrase. Hypothesis reasons remain authored prose. Extracted JavaScript strings and comments, HTML comments and structured cells cannot qualify as page furniture. Embedded map data must use strict JSON to retain structured citation handling; JavaScript object syntax still receives writing checks. Authored claims and repeated explanations remain subject to the repetition check.
