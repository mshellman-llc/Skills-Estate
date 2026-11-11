# Salesforce org preflight

Check an exact intended Salesforce org before a write. The script can query an explicit CLI connection or validate a fresh connector response. It refuses a missing target and keeps identity checks separate from write authorization.

[SKILL.md](SKILL.md) describes the workflow, private registry, receipt format, and offline tests. Python 3 is required; Salesforce CLI is required only for live CLI queries.
