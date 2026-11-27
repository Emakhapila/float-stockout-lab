# DL-002: What "one level up" from project 1 means

- **Date:** 2026-11-24
- **Status:** Accepted

## Context

Project 1 (Kenya Food Security Risk Index) already shows a dbt pipeline, a
pre-stated validation test, a point forecast against a baseline, scheduled
automation, a dashboard and a decision log. Repeating those adds little. This
project should be visibly harder, in ways a senior reviewer would recognise.

## Decision

| Area | Project 1 | This project |
|---|---|---|
| Validation | One pre-stated test against IPC | **Calibrate the method itself**: run the full analysis on hundreds of simulated experiments with known truth and report false-positive rate, power and interval coverage |
| Honesty mechanism | Written-down test | **Blinded analysis**: true parameters hidden behind a hash commitment until the pre-registered analysis has run |
| Causal inference | None | Cluster-randomised design, power by simulation, CUPAC, SRM, novelty and spillover checks |
| Forecasting | Point forecast vs baseline | Probabilistic forecast, conformal intervals, coverage, and a cost-based alert threshold |
| AI | None | Tool-using reviewer with code-enforced guardrails, scored against a rule-based baseline on planted problems |
| Engineering | Scripts and notebooks | Installable typed package, Pydantic contracts, strict mypy, tests with 80%+ coverage, CI on Linux and Windows, pre-commit |

## Cost

These raise the v1 estimate from about 95 h to about **110 h** (calibration
study +10 h, engineering standards +5 h): roughly 25 working days, or 5 to
5.5 weeks at 4–4.5 h a day.

## What gets cut first if time runs short

1. Reviewer eval: 40 scenarios down to 20.
2. Calibration study: 500 runs down to 200, fewer scenarios.
3. Forecast: drop statsforecast, keep seasonal naive + quantile LightGBM.

Experiment depth and blinding are not cut.
