# Method and implementation

A reusable skill needs enough method to make the right decisions and enough implementation to produce its promised result. Preserve both when converting an existing estate. Removing scripts or templates can leave a readable description that cannot do the work.

## Separate the decisions from the configuration

Keep the durable method in the entrypoint or a focused reference: the questions to resolve, the evidence to use, the decision criteria, the sequence of handoffs, and the failure conditions. Explain why a choice changes the result. Frameworks and taxonomies are useful when they guide those decisions.

Keep concrete implementation in scripts, templates or adapters that the workflow actually calls. A Python document renderer, a JavaScript interface, a Salesforce deployment helper or a platform-specific schema can be a legitimate part of a skill. Name its dependencies and test its output. Do not make a working implementation private merely because it uses a particular stack.

Put variable project choices in configuration. Branding belongs in the selected shared profile. Resolve source roots and credentials through the host's supported mechanisms. Keep private client records outside reusable packages. A configured integration still needs a successful operation before the workflow can claim it worked.

## Choose an implementation that fits the task

For a general design method, describe the required behavior and let the agent choose among available tools. An example in React should illustrate the method without making React a prerequisite for a request that can be completed elsewhere.

For a task that promises an executable output, preserve the code needed to produce that output. State when that path applies. If another host lacks the runtime, test an adapter or another implementation against the same outcome. Do not replace a generated spreadsheet with a prose description and call the two equivalent.

For a platform operation, retain the platform's actual commands and contracts. A Salesforce skill can support offline metadata preparation alongside a deployment path that needs a confirmed org. The offline output does not establish deployment success.

## Worked boundary example

A proposal skill owns the scope comparison and price reconciliation. Its Python builder reads sourced option data and emits a standalone HTML page. The page's option selector is part of the deliverable, so the JavaScript that updates scope, price and team belongs in the package.

The client's colors and fonts come from a shared brand profile. Private quote data stays with the project. The package can include a synthetic quote fixture that exercises the builder. Tests check that each selected option displays its own figures and preserves its exclusions. A PDF export also needs a page review.

This division preserves a working proposal while allowing another client or host to supply different inputs. The comparison method remains available even when the author chooses another renderer.

## Audit an existing skill

1. Follow every promised output back to the instructions and resources that produce it. Keep the scripts and templates that are still necessary.
2. Find company names, absolute paths and service assumptions. Replace variable settings with explicit configuration. Preserve any genuine platform requirement.
3. Inspect cross-skill calls. Bundle a required runtime dependency or provide a tested way to resolve it. An unavailable tool name is not an adapter.
4. Run representative tasks from an isolated package. Compare the outputs with the source material and preserve failed attempts.
5. Compare host results before claiming parity. A portable file layout is only the starting point for that test.

Keep substantial conditional material in references and load it when needed. Progressive disclosure controls context size; it is not a reason to delete the implementation. Review stale dependencies when their interfaces change and retain exact source provenance for the repair.
