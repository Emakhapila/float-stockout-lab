# DL-001: Business question and data strategy

- **Date:** 2026-11-24
- **Status:** Accepted

## Context

Fintech customer data is private, and most public fintech datasets are built
for fraud detection. I want one project in which an A/B test, a transaction
forecast and an AI component all serve a single business decision, in a
problem that matters for mobile money in Africa.

## Decision

**Business question.** Should a mobile money operator roll out
forecast-triggered "rebalance now" alerts to its agents, and if so, to which
agents?

Agents who run out of e-float or cash fail customers' cash-outs. Customers
then walk to another agent or give up. Rural customers, who often have one
nearby agent, are likely hit hardest.

**Data.** A synthetic agent-day panel, calibrated to public aggregates, with
the true effects drawn at random and sealed before I analyse anything
(see `sealed/README.md`).

| Source | Used for | Licence / terms | Status |
|---|---|---|---|
| CBK mobile payments statistics | Agent counts, monthly volume and value, giving per-agent daily averages | Check CBK website terms; cite the source | To verify |
| FinAccess Household Survey 2024 | Urban/rural usage and access patterns | Check publication terms; cite | To verify |
| World Bank Global Findex | Gender and income gaps in account use | Check current licence on the Findex data page | To verify |
| PaySim (Kaggle) | Background reading only. No rows used | CC BY-SA 4.0: derived data would have to be shared alike | Not used as data |

Only aggregates are used for calibration. No raw rows from any source enter
the repo.

## Alternatives considered

1. **PaySim as the main dataset.** Rejected: it models fraud, covers about one
   month, and has no agent float, so it cannot answer this question. Its
   share-alike licence would also bind derived data.
2. **Public aggregates only.** Rejected: monthly national totals cannot support
   an agent-level experiment or forecast.
3. **Synthetic without blinding.** Rejected: "you built the data, so of course
   you found the effect" would be a fair objection. Sealing the truth answers
   it.

## Consequences

- The project validates the *analysis method*, not a real-world effect size.
  The README and memo must say so plainly.
- Calibration targets and their sources are written down before the simulator
  is built, so the realism claims can be checked.
- In the write-up, "agent" means a mobile money agent. The AI component is
  called "the reviewer".
