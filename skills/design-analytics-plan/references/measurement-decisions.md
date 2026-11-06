# Measurement decisions

## Define the decision before the metric

Identify who will use the information and what they can change. A delivery-information page might need to answer whether shoppers reach the relevant information before starting checkout. Use the actual product question. Do not assume a SaaS activation or retention funnel for an unrelated business.

Define the unit being counted. A page view, visit, session, order, and person are different units. If the approved data contains anonymous page events, do not call a unique event count “customers.” Define the denominator and time window before reporting a rate. If repeat visits cannot be separated under the approved policy, state that limitation at the affected metric.

Specify exclusions such as test traffic or duplicate delivery when evidence and the system support them. Describe late-arriving data and time-zone handling where they affect the decision. Use the existing source of truth rather than creating another definition silently.

## Keep the event catalog small

For each event, record its decision or metric, trigger, allowed properties, source, destination, ownership, retention, verification method, and current state. Use only the fields the system needs; unknown fields stay pending. Names should describe actual behavior rather than an inferred intent. Rendering a button is not a completed purchase.

Review properties against the approved policy. An anonymous plan may need only an event name, a safe route category, and a coarse time bucket. The exact policy controls that choice. A persistent identifier can still link behavior even if it does not contain a person's name. Do not introduce cross-session linking merely to make a funnel calculation convenient.

Free-text responses, search terms, query strings, and full URLs need particular scrutiny. They can carry personal details, secrets, or customer content. Prefer a controlled category when the decision can be answered with it. Keep private sample payloads out of reusable skill files and public reports.

## Verify data before interpreting it

For an implemented event, define a controlled action and the expected payload. Check its delivery at the actual destination, frequency, and absence when the action does not occur. Check retries, duplicate events, consent behavior when applicable, and unexpected properties. Use a safe test path or test environment; measurement verification does not authorize a real charge or an external submission.

Record which destination was observed and when. A code change supports “implemented locally.” A dashboard mockup supports “proposed view.” Delivery receipts and queries can support a verified event for the tested conditions. None of these states should be inferred from the plan alone.

## Read results within their limits

An observed rate change can reflect traffic mix, seasonality, instrumentation, or the product change. Do not assign cause from timing alone. Report the source and comparison window. A causal impact claim needs a suitable experimental or other justified design with its assumptions. Attribution models require their own definitions and limits.

If historical data is unavailable, deliver the definitions and a proposed baseline-collection period, with timing identified as a proposal. Keep numerical targets pending until supported or explicitly chosen by the user.
