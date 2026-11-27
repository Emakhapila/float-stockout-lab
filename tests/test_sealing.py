import json
from pathlib import Path

import numpy as np
import pytest

from floatlab import sealing
from floatlab.schemas import TrueParams


def test_seal_then_verify_roundtrip(tmp_path: Path) -> None:
    digest = sealing.seal(tmp_path)
    assert (tmp_path / sealing.COMMITMENT_FILE).read_text().strip() == digest
    assert isinstance(sealing.verify(tmp_path), TrueParams)


def test_tampering_is_detected(tmp_path: Path) -> None:
    sealing.seal(tmp_path)
    path = tmp_path / sealing.PARAMS_FILE
    payload = json.loads(path.read_text())
    payload["params"]["relative_effect"] = -0.99
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="Commitment mismatch"):
        sealing.verify(tmp_path)


def test_reseal_refused_without_overwrite(tmp_path: Path) -> None:
    sealing.seal(tmp_path)
    with pytest.raises(FileExistsError):
        sealing.seal(tmp_path)
    sealing.seal(tmp_path, overwrite=True)


def test_salt_makes_commitments_unique(tmp_path: Path) -> None:
    a = sealing.seal(tmp_path / "a")
    b = sealing.seal(tmp_path / "b")
    assert a != b


def test_priors_include_null_effects() -> None:
    rng = np.random.default_rng(0)
    draws = [sealing.draw_true_params(rng) for _ in range(500)]
    null_share = sum(d.relative_effect == 0.0 for d in draws) / len(draws)
    assert 0.12 < null_share < 0.28


def test_cli_seal_and_verify(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    sealing.main(["seal", "--dir", str(tmp_path)])
    sealing.main(["verify", "--dir", str(tmp_path)])
    out = capsys.readouterr().out
    assert "Sealed." in out and "verified" in out
    assert "relative_effect" not in out  # never print the secret
