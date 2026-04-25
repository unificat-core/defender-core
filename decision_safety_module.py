from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Sequence, Tuple


class Mode(str, Enum):
    NORMAL = "NORMAL"
    AUTOPILOT = "AUTOPILOT"
    SURVIVAL = "SURVIVAL"
    FULL_SURVIVAL = "FULL_SURVIVAL"


class State(str, Enum):
    STABLE = "STABLE"
    WARNING = "WARNING"
    RISK = "RISK"
    SURVIVAL = "SURVIVAL"


class GateAction(str, Enum):
    STOP = "STOP"
    HOLD = "HOLD"
    BUILD_FIRST = "BUILD_FIRST"
    DROP = "DROP"
    ALLOW = "ALLOW"


@dataclass(frozen=True)
class Signal:
    """Single signal delivered to the Priority Engine."""

    name: str
    relevance: float
    intensity: float
    confidence: float
    metadata: Dict[str, float] = field(default_factory=dict)


@dataclass
class SystemSnapshot:
    """Internal runtime state used by Decision Safety Module."""

    mode: Mode = Mode.NORMAL
    state: State = State.STABLE
    previous_score: float = 100.0
    current_score: float = 100.0
    critical_point: bool = False
    preemptive_adjustment: bool = False
    system_state: str = "HEALTHY"
    constraints: List[str] = field(default_factory=list)


class DecisionSafetyModule:
    """
    PRS runtime control layer.

    Global rule: system cannot progress if previous layer is not stable.
    Decision Gate is mandatory and cannot be skipped.
    """

    def __init__(
        self,
        relevance_threshold: float = 0.35,
        tension_threshold: float = 0.65,
        score_recovery_threshold: int = 4,
        gate_threshold: int = 2,
    ) -> None:
        self.relevance_threshold = relevance_threshold
        self.tension_threshold = tension_threshold
        self.score_recovery_threshold = score_recovery_threshold
        self.gate_threshold = gate_threshold
        self.snapshot = SystemSnapshot()

    # 1) PRIORITY ENGINE
    def _compute_weight(self, signal: Signal) -> float:
        return max(0.0, signal.relevance) * 0.5 + max(0.0, signal.intensity) * 0.3 + max(0.0, signal.confidence) * 0.2

    def _select_active_signal(self, signals: Sequence[Signal]) -> Optional[Signal]:
        weighted: List[Tuple[Signal, float]] = []
        for signal in signals:
            if signal.relevance < self.relevance_threshold:
                continue
            weighted.append((signal, self._compute_weight(signal)))

        if not weighted:
            return None

        return max(weighted, key=lambda item: item[1])[0]

    # 2) FUNCTION CHECK
    def _check_function_integrity(
        self,
        *,
        detect: bool,
        awareness: bool,
        tension: float,
        regulation_possible: bool,
        decision_possible: bool,
    ) -> Mode:
        presence_ok = detect and awareness
        rhythm_ok = (tension <= self.tension_threshold) and regulation_possible
        structure_ok = decision_possible

        if not presence_ok:
            return Mode.AUTOPILOT
        if not rhythm_ok:
            return Mode.SURVIVAL
        if not structure_ok:
            return Mode.FULL_SURVIVAL
        return Mode.NORMAL

    # 3) FAIL PATH
    def _apply_fail_path(self, mode: Mode) -> Dict[str, object]:
        constraints: List[str] = []
        action = "IGNORE"

        if mode == Mode.AUTOPILOT:
            constraints.append("fallback_to_patterns")
            action = "DELAY"
        elif mode == Mode.SURVIVAL:
            constraints.extend(["single_signal_only", "force_pause"])
            action = "DELAY"
        elif mode == Mode.FULL_SURVIVAL:
            constraints.extend(["disable_decision", "allow_only:ACT/DELAY/IGNORE"])
            action = "DELAY"

        self.snapshot.constraints = constraints
        return {
            "type": "reactive_or_limited_response",
            "mode": mode.value,
            "constraints": constraints,
            "action": action,
        }

    # 4) SCORING
    @staticmethod
    def _map_state(score: float) -> State:
        if score >= 80:
            return State.STABLE
        if score >= 50:
            return State.WARNING
        if score >= 20:
            return State.RISK
        return State.SURVIVAL

    def _score_system(self, p_score: float, r_score: float, s_score: float) -> Tuple[float, State]:
        total = min(p_score, r_score, s_score)
        return total, self._map_state(total)

    # 5) TEMPORAL ENGINE
    def _temporal_assessment(self, current_score: float, pattern_detected: bool, recovery_time: int) -> None:
        delta = current_score - self.snapshot.previous_score
        self.snapshot.critical_point = delta < -20
        self.snapshot.preemptive_adjustment = pattern_detected

        if recovery_time > self.score_recovery_threshold:
            self.snapshot.system_state = "STRAINED"
        else:
            self.snapshot.system_state = "HEALTHY"

        self.snapshot.previous_score = current_score

    # 6) MODE ADJUSTMENT
    def _apply_mode_adjustment(self, state: State, preemptive_adjustment: bool) -> List[str]:
        actions: List[str] = []

        if state == State.WARNING:
            actions.extend(["slow_down", "force_presence_check"])
        elif state == State.RISK:
            actions.extend(["single_signal_only", "limit_decisions"])

        if preemptive_adjustment:
            actions.append("reduce_complexity")

        return actions

    # 7) DECISION GATE (MANDATORY)
    def _decision_gate(self, p: int, r: int, s: int, d: int) -> GateAction:
        if p <= self.gate_threshold:
            return GateAction.STOP
        if r <= self.gate_threshold:
            return GateAction.HOLD
        if s <= self.gate_threshold:
            return GateAction.BUILD_FIRST
        if d <= self.gate_threshold:
            return GateAction.DROP
        return GateAction.ALLOW

    # 8) PRS PIPELINE
    def _classify_signal(self, active_signal: Signal) -> str:
        is_high_urgency = active_signal.relevance >= 0.75 and active_signal.intensity >= 0.75
        if is_high_urgency and active_signal.confidence < 0.5:
            return "FALSE_ALARM"
        if is_high_urgency and active_signal.confidence >= 0.5:
            return "REAL_THREAT"
        if active_signal.relevance >= 0.5:
            return "INFO"
        return "NOISE"

    def _prs_pipeline(self, active_signal: Signal, classification: str) -> Dict[str, object]:
        if classification == "REAL_THREAT":
            action = "ACT"
        elif classification == "INFO":
            action = "PROCESS"
        else:
            action = "IGNORE"

        return {
            "presence": "detect+validate",
            "rhythm": ["micro_pause", "adjust_bandwidth"],
            "structure": {
                "classification": classification,
                "action": action,
                "execute": True,
            },
        }

    def run(
        self,
        *,
        signals: Sequence[Signal],
        detect: bool,
        awareness: bool,
        tension: float,
        regulation_possible: bool,
        decision_possible: bool,
        p_score: float,
        r_score: float,
        s_score: float,
        pattern_detected: bool,
        recovery_time: int,
        gate_p: int,
        gate_r: int,
        gate_s: int,
        gate_d: int,
    ) -> Dict[str, object]:
        """Full Decision Safety flow (steps 0-10)."""
        # 0 + 1
        active_signal = self._select_active_signal(signals)
        if active_signal is None:
            return {
                "selected_signal": None,
                "classification": "NO_SIGNAL",
                "mode": self.snapshot.mode.value,
                "response": {"type": "conscious", "action": "IGNORE"},
                "reason": "no_relevant_signal",
            }
        classification = self._classify_signal(active_signal)

        # 2
        mode = self._check_function_integrity(
            detect=detect,
            awareness=awareness,
            tension=tension,
            regulation_possible=regulation_possible,
            decision_possible=decision_possible,
        )
        self.snapshot.mode = mode

        # 3
        if mode != Mode.NORMAL:
            return {
                "selected_signal": active_signal.name,
                "classification": classification,
                "mode": mode.value,
                "response": self._apply_fail_path(mode),
                "stopped": True,
            }

        # 4
        total_score, state = self._score_system(p_score, r_score, s_score)
        self.snapshot.current_score = total_score
        self.snapshot.state = state

        # 5
        self._temporal_assessment(total_score, pattern_detected, recovery_time)

        # 6
        adjustments = self._apply_mode_adjustment(state, self.snapshot.preemptive_adjustment)

        # 7
        gate = self._decision_gate(gate_p, gate_r, gate_s, gate_d)
        if gate != GateAction.ALLOW:
            return {
                "selected_signal": active_signal.name,
                "classification": classification,
                "mode": mode.value,
                "state": state.value,
                "gate": gate.value,
                "adjustments": adjustments,
                "temporal": {
                    "critical_point": self.snapshot.critical_point,
                    "preemptive_adjustment": self.snapshot.preemptive_adjustment,
                    "system_state": self.snapshot.system_state,
                },
                "stopped": True,
            }

        # 8 + 9
        pipeline = self._prs_pipeline(active_signal, classification)
        return {
            "selected_signal": active_signal.name,
            "classification": classification,
            "mode": mode.value,
            "state": state.value,
            "score": total_score,
            "critical_point": self.snapshot.critical_point,
            "system_state": self.snapshot.system_state,
            "temporal": {
                "critical_point": self.snapshot.critical_point,
                "preemptive_adjustment": self.snapshot.preemptive_adjustment,
                "system_state": self.snapshot.system_state,
            },
            "adjustments": adjustments,
            "gate": gate.value,
            "pipeline": pipeline,
            "response": {
                "type": "conscious",
                "action": pipeline["structure"]["action"],
                "executed": True,
            },
            "stopped": False,
        }


def run_mvp(signals: Sequence[Signal], pause_seconds: float = 0.2) -> Dict[str, object]:
    """Step 14 MVP: select signal -> pause -> check P/R/S -> act."""
    import time

    module = DecisionSafetyModule()
    active_signal = module._select_active_signal(signals)
    if active_signal is None:
        return {"status": "NO_SIGNAL"}

    time.sleep(max(0.0, pause_seconds))

    # Simple P/R/S check in MVP mode
    p_ok = active_signal.confidence >= 0.5
    r_ok = active_signal.intensity <= 0.85
    s_ok = active_signal.relevance >= module.relevance_threshold

    if not (p_ok and r_ok and s_ok):
        return {"status": "BLOCKED", "signal": active_signal.name}

    return {"status": "ACT", "signal": active_signal.name}
