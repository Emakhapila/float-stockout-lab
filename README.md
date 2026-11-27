# Float Stockout Lab

**Should a mobile money operator send agents forecast-triggered "rebalance now"
alerts, and to which agents?**

When a mobile money agent runs out of e-float or cash, a customer's cash-out
fails. This project builds a calibrated simulation of an agent network, tests
an alert policy with a cluster-randomised experiment, forecasts cash-out
demand with honest uncertainty, and uses an AI reviewer to audit the
experiment before a decision memo goes to a non-technical stakeholder.

> **Status:** in progress (v1). The true effect sizes are sealed; see
> [`sealed/`](sealed/README.md).

## How the parts connect

| Part | Role |
|---|---|
| Simulator | Agent-day panel calibrated to public aggregates, with planted problems and sealed ground truth |
| Experiment | Tests the alert policy. Cluster randomisation, power by simulation, CUPAC, SRM/novelty/spillover checks |
| Forecast | Predicts demand with intervals; triggers the alert; supplies the CUPAC covariate |
| Reviewer | Audits the experiment with read-only tools and drafts the memo. Never decides |

## Repository layout

```
src/floatlab/
  schemas.py      data contracts (defined first)
  sealing.py      blinding: seal, commit hash, verify
  simulate/       synthetic panel
  experiment/     design, power, analysis, checks
  forecast/       baselines, probabilistic models, backtest
  reviewer/       tools, loop, guardrails, eval
docs/
  decision_log/   DL-001, DL-002, ...
  preregistration/
sealed/           COMMITMENT.sha256 (true params stay local until unsealing)
tests/
```

## Setup (Windows, no admin rights)

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev]"
pre-commit install
pytest
```

## Decision log

- [DL-001](docs/decision_log/DL-001-business-question-and-data.md): business question and data strategy
- [DL-002](docs/decision_log/DL-002-level-up-standard.md): what "one level up" means for this project

## Limitations

This project validates an analysis pipeline on simulated data. It does not
estimate the real-world effect of alerts on any operator's network.
(Expanded as the project develops.)
