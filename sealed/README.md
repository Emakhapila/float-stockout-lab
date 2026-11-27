# Sealed ground truth

The simulator's true effect sizes are drawn at random and hidden from me until
the pre-registered analysis has run.

| File | Committed? | Purpose |
|---|---|---|
| `COMMITMENT.sha256` | Yes, before the pre-registration | SHA-256 of the salted parameters |
| `true_params.json` | **No** until unsealing (git-ignored, blocked by a pre-commit hook) | The actual parameters |

Order of operations:

1. `python -m floatlab.sealing seal`
2. Commit `COMMITMENT.sha256`.
3. Write and tag the pre-registration.
4. Run the analysis exactly as pre-registered.
5. `python -m floatlab.sealing verify`, then commit `true_params.json` and compare.

If the sealed file is lost before step 5, the blind is broken. Record it in the
decision log rather than re-sealing quietly.
