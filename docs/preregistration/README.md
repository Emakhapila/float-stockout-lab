# Pre-registration

The pre-registration is written after the parameters are sealed and before any
experiment-period data is analysed. It is frozen with a git tag
(`prereg-v1`) and, optionally, mirrored on OSF for an independent timestamp.

It will specify:

- Hypothesis and primary metric (cash-out failure rate per agent-day)
- Guardrails, including no worsening for rural agents
- Unit of randomisation (cluster) and assignment procedure
- Sample size from the power simulation, with the assumed ICC
- Analysis model, covariates (CUPAC) and standard errors
- Stopping rule (fixed horizon in v1)
- Subgroups, decision rule and what counts as "ship", "don't ship" and "inconclusive"
- Planned checks: SRM, novelty, spillover

Any later change is a dated amendment below the original, never an edit.
