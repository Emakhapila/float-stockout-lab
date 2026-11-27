"""Blinding: seal the true parameters, commit only their hash, unseal later.

Workflow
--------
1. ``python -m floatlab.sealing seal`` draws TrueParams from wide priors with
   an OS-random seed, writes ``sealed/true_params.json`` (git-ignored) and
   ``sealed/COMMITMENT.sha256`` (committed).
2. Commit the hash *before* writing the pre-registration.
3. After the pre-registered analysis has run, ``python -m floatlab.sealing
   verify`` proves the parameters were not changed, and they are published.

A random salt is included in the hashed payload so the hash cannot be
reversed by brute-forcing likely parameter values.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import secrets
from pathlib import Path
from typing import Any

import numpy as np

from floatlab.schemas import TrueParams

SEALED_DIR = Path("sealed")
PARAMS_FILE = "true_params.json"
COMMITMENT_FILE = "COMMITMENT.sha256"


def draw_true_params(rng: np.random.Generator) -> TrueParams:
    """Draw ground truth from deliberately wide priors.

    A null effect is possible on purpose: about 20% of draws have no effect,
    so the analyst cannot assume there is something to find.
    """
    null_effect = rng.random() < 0.20
    relative_effect = 0.0 if null_effect else float(rng.uniform(-0.40, 0.05))
    novelty = rng.random() < 0.5
    return TrueParams(
        relative_effect=round(relative_effect, 4),
        rural_effect_multiplier=round(float(rng.uniform(0.0, 1.5)), 4),
        icc=round(float(rng.uniform(0.02, 0.20)), 4),
        novelty_half_life_days=round(float(rng.uniform(7, 28)), 2) if novelty else None,
        spillover_share=round(float(rng.uniform(0.0, 0.5)), 4),
    )


def _canonical_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def commitment_for(payload: dict[str, Any]) -> str:
    """SHA-256 hex digest of the canonical JSON payload."""
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def seal(directory: Path = SEALED_DIR, *, overwrite: bool = False) -> str:
    """Draw, write and hash the true parameters. Returns the commitment."""
    directory.mkdir(parents=True, exist_ok=True)
    params_path = directory / PARAMS_FILE
    if params_path.exists() and not overwrite:
        raise FileExistsError(
            f"{params_path} already exists. Re-sealing would break the blind; "
            "pass overwrite=True only before anything has been committed."
        )
    seed = secrets.randbits(64)
    params = draw_true_params(np.random.default_rng(seed))
    payload = {"salt": secrets.token_hex(16), "seed": seed, "params": params.model_dump()}
    params_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    digest = commitment_for(payload)
    (directory / COMMITMENT_FILE).write_text(digest + "\n", encoding="utf-8")
    return digest


def verify(directory: Path = SEALED_DIR) -> TrueParams:
    """Check the sealed file against the committed hash and return the params."""
    payload = json.loads((directory / PARAMS_FILE).read_text(encoding="utf-8"))
    expected = (directory / COMMITMENT_FILE).read_text(encoding="utf-8").strip()
    actual = commitment_for(payload)
    if actual != expected:
        raise ValueError(f"Commitment mismatch: expected {expected}, got {actual}")
    return TrueParams.model_validate(payload["params"])


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Seal or verify the true parameters.")
    parser.add_argument("command", choices=["seal", "verify"])
    parser.add_argument("--dir", type=Path, default=SEALED_DIR)
    args = parser.parse_args(argv)
    if args.command == "seal":
        digest = seal(args.dir)
        print(f"Sealed. Commit {args.dir / COMMITMENT_FILE} now: {digest}")
        print("Do NOT open true_params.json until the pre-registered analysis has run.")
    else:
        verify(args.dir)
        print("Commitment verified: parameters unchanged since sealing.")


if __name__ == "__main__":  # pragma: no cover
    main()
