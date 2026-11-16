# Automations

Separate definition, activation, execution, and verified outcome. Creating or
enabling an automation proves only that its definition is active. It does not
prove the first scheduled run succeeded.

Record the schedule, target, authority boundary, notification policy, and safe
failure behavior. Verify the saved definition after creation. When the finish
line requires working behavior, observe a real run and its destination result.
Do not simulate success or treat an unchanged external state as a failure.

Report `active-unobserved` until a run is seen, then name the run receipt and
the artifact or state it produced.
