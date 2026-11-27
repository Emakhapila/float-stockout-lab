from datetime import date

import pytest
from pydantic import ValidationError

from floatlab.schemas import AgentDay, Arm, Locality, SimulationConfig, TrueParams


def _row(**overrides: object) -> AgentDay:
    base: dict[str, object] = {
        "agent_id": "A0001",
        "cluster_id": "C001",
        "day": date(2025, 3, 31),
        "locality": Locality.RURAL,
        "arm": Arm.TREATMENT,
        "opening_efloat_kes": 40_000,
        "opening_cash_kes": 25_000,
        "cash_out_requests": 20,
        "cash_out_requested_kes": 60_000,
        "failed_cash_outs": 3,
        "alert_sent": True,
        "rebalance_trips": 1,
    }
    base.update(overrides)
    return AgentDay.model_validate(base)


def test_valid_row_and_failure_rate() -> None:
    assert _row().failure_rate == pytest.approx(0.15)


def test_failure_rate_is_none_without_requests() -> None:
    assert _row(cash_out_requests=0, failed_cash_outs=0).failure_rate is None


def test_failed_cannot_exceed_requests() -> None:
    with pytest.raises(ValidationError, match="cannot exceed"):
        _row(failed_cash_outs=21)


def test_control_never_alerted() -> None:
    with pytest.raises(ValidationError, match="never receive alerts"):
        _row(arm=Arm.CONTROL, alert_sent=True)


def test_negative_money_rejected() -> None:
    with pytest.raises(ValidationError):
        _row(opening_cash_kes=-1)


def test_rows_are_immutable() -> None:
    row = _row()
    with pytest.raises(ValidationError):
        row.failed_cash_outs = 0  # type: ignore[misc]


def test_simulation_config_defaults_valid() -> None:
    cfg = SimulationConfig()
    assert sum(cfg.locality_shares.values()) == pytest.approx(1.0)


def test_simulation_config_rejects_bad_shares() -> None:
    with pytest.raises(ValidationError, match="sum to 1"):
        SimulationConfig(locality_shares={Locality.URBAN: 0.5, Locality.RURAL: 0.4})


def test_simulation_config_rejects_bad_cluster_sizes() -> None:
    with pytest.raises(ValidationError, match="agents_per_cluster_min"):
        SimulationConfig(agents_per_cluster_min=10, agents_per_cluster_max=5)


def test_true_params_bounds() -> None:
    with pytest.raises(ValidationError):
        TrueParams(relative_effect=0.1, rural_effect_multiplier=1.0, icc=1.0, spillover_share=0.1)
