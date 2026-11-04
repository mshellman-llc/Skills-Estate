# Deployments

Name the target environment before acting. Development, staging, and production
are different states. A local build or successful validation does not prove a
deployment.

Require the destination system's deployment receipt or job result. Run the
target's required tests, then verify the deployed component or endpoint in that
environment. Production deployment, rollback, permission changes, and external
notifications require the authority defined by the current task and repository.

Report the environment, deployment identifier, tests, live check, and every
higher environment left unchanged.
