"""Data contracts for floatlab.

Definition first: every table the simulator writes and every config the
analysis reads is defined here before any logic uses it. The same models
become the request/response schemas of the v2 API.

Units: money in Kenyan shillings (KES), whole numbers. Dates are calendar
days in Africa/Nairobi.
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Locality(StrEnum):
    """Where an agent operates. Drives demand level and rebalancing distance."""

    URBAN = "urban"
    PERI_URBAN = "peri_urban"
    RURAL = "rural"


class Arm(StrEnum):
    """Experiment arm, assigned at cluster level."""

    CONTROL = "control"
    TREATMENT = "treatment"


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


# --------------------------------------------------------------------------
# Simulator output: one row per agent per day
# --------------------------------------------------------------------------


class AgentDay(_Frozen):
    """One mobile money agent on one day. Grain of the core fact table."""

    agent_id: str = Field(min_length=1)
    cluster_id: str = Field(min_length=1, description="Market/town; unit of randomisation")
    day: date
    locality: Locality
    arm: Arm
    opening_efloat_kes: int = Field(ge=0)
    opening_cash_kes: int = Field(ge=0)
    cash_out_requests: int = Field(ge=0)
    cash_out_requested_kes: int = Field(ge=0)
    failed_cash_outs: int = Field(ge=0, description="Requests the agent could not serve")
    alert_sent: bool
    rebalance_trips: int = Field(ge=0)

    @model_validator(mode="after")
    def _check_consistency(self) -> AgentDay:
        if self.failed_cash_outs > self.cash_out_requests:
            raise ValueError("failed_cash_outs cannot exceed cash_out_requests")
        if self.alert_sent and self.arm is Arm.CONTROL:
            raise ValueError("control agents never receive alerts")
        return self

    @property
    def failure_rate(self) -> float | None:
        """Primary metric at row level. None when there were no requests."""
        if self.cash_out_requests == 0:
            return None
        return self.failed_cash_outs / self.cash_out_requests


# --------------------------------------------------------------------------
# Configs
# --------------------------------------------------------------------------


class SimulationConfig(_Frozen):
    """Public knobs of the simulator. Committed to the repo; not secret."""

    n_clusters: int = Field(default=120, ge=4)
    agents_per_cluster_min: int = Field(default=3, ge=1)
    agents_per_cluster_max: int = Field(default=15, ge=1)
    locality_shares: dict[Locality, float] = Field(
        default_factory=lambda: {
            Locality.URBAN: 0.35,
            Locality.PERI_URBAN: 0.30,
            Locality.RURAL: 0.35,
        }
    )
    start_day: date = date(2025, 1, 1)
    pre_period_days: int = Field(default=365, ge=28, description="History for forecast/CUPAC")
    experiment_days: int = Field(default=56, ge=7)
    seed: int = 20261124

    @model_validator(mode="after")
    def _check(self) -> SimulationConfig:
        if self.agents_per_cluster_min > self.agents_per_cluster_max:
            raise ValueError("agents_per_cluster_min must be <= agents_per_cluster_max")
        if abs(sum(self.locality_shares.values()) - 1.0) > 1e-9:
            raise ValueError("locality_shares must sum to 1")
        return self


class TrueParams(_Frozen):
    """The ground truth the analysis must recover.

    Drawn at random, written to sealed/true_params.json and committed only
    as a SHA-256 hash until the pre-registered analysis has run.
    """

    relative_effect: float = Field(
        ge=-1.0, le=1.0, description="Relative change in failure rate (negative = fewer failures)"
    )
    rural_effect_multiplier: float = Field(
        ge=0.0, le=3.0, description="Rural effect = relative_effect * this"
    )
    icc: float = Field(gt=0.0, lt=1.0, description="Intra-cluster correlation of failure rate")
    novelty_half_life_days: float | None = Field(
        default=None, gt=0.0, description="None = no novelty decay"
    )
    spillover_share: float = Field(
        ge=0.0, le=1.0, description="Share of failed demand that moves to a nearby agent"
    )
