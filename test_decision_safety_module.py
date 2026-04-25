import unittest
import random
import time

from decision_safety_module import DecisionSafetyModule, GateAction, Signal, run_mvp


class DecisionSafetyModuleTests(unittest.TestCase):
    def test_fail_path_when_presence_missing(self):
        module = DecisionSafetyModule()
        result = module.run(
            signals=[Signal(name="alert", relevance=0.8, intensity=0.4, confidence=0.9)],
            detect=False,
            awareness=True,
            tension=0.2,
            regulation_possible=True,
            decision_possible=True,
            p_score=90,
            r_score=85,
            s_score=88,
            pattern_detected=False,
            recovery_time=1,
            gate_p=3,
            gate_r=3,
            gate_s=3,
            gate_d=3,
        )

        self.assertTrue(result["stopped"])
        self.assertEqual(result["response"]["mode"], "AUTOPILOT")

    def test_gate_blocks_when_d_is_low(self):
        module = DecisionSafetyModule(gate_threshold=1)
        result = module.run(
            signals=[Signal(name="intel", relevance=0.9, intensity=0.3, confidence=0.9)],
            detect=True,
            awareness=True,
            tension=0.1,
            regulation_possible=True,
            decision_possible=True,
            p_score=90,
            r_score=90,
            s_score=90,
            pattern_detected=False,
            recovery_time=1,
            gate_p=2,
            gate_r=2,
            gate_s=2,
            gate_d=1,
        )

        self.assertTrue(result["stopped"])
        self.assertEqual(result["gate"], GateAction.DROP.value)

    def test_successful_allow_flow(self):
        module = DecisionSafetyModule(gate_threshold=1)
        result = module.run(
            signals=[Signal(name="threat", relevance=0.95, intensity=0.9, confidence=0.9)],
            detect=True,
            awareness=True,
            tension=0.2,
            regulation_possible=True,
            decision_possible=True,
            p_score=95,
            r_score=90,
            s_score=92,
            pattern_detected=True,
            recovery_time=2,
            gate_p=2,
            gate_r=2,
            gate_s=2,
            gate_d=2,
        )

        self.assertFalse(result["stopped"])
        self.assertEqual(result["selected_signal"], "threat")
        self.assertEqual(result["classification"], "REAL_THREAT")
        self.assertEqual(result["mode"], "NORMAL")
        self.assertEqual(result["gate"], GateAction.ALLOW.value)
        self.assertEqual(result["response"]["action"], "ACT")

    def test_mvp(self):
        result = run_mvp([Signal(name="focus", relevance=0.8, intensity=0.4, confidence=0.8)], pause_seconds=0)
        self.assertEqual(result["status"], "ACT")

    def test_fear_false_alarm_should_not_act(self):
        module = DecisionSafetyModule(gate_threshold=1)

        result = module.run(
            signals=[Signal(name="fear_signal", relevance=0.9, intensity=0.9, confidence=0.2)],
            detect=True,
            awareness=True,
            tension=0.4,
            regulation_possible=True,
            decision_possible=True,
            p_score=80,
            r_score=60,
            s_score=70,
            pattern_detected=False,
            recovery_time=2,
            gate_p=2,
            gate_r=2,
            gate_s=2,
            gate_d=2,
        )

        self.assertEqual(result["selected_signal"], "fear_signal")
        self.assertEqual(result["mode"], "NORMAL")
        self.assertEqual(result["classification"], "FALSE_ALARM")
        self.assertNotEqual(result["response"]["action"], "ACT")

    def test_survival_mode_limits_action(self):
        module = DecisionSafetyModule()

        result = module.run(
            signals=[Signal(name="urgent", relevance=0.9, intensity=0.9, confidence=0.9)],
            detect=True,
            awareness=True,
            tension=0.95,
            regulation_possible=False,
            decision_possible=True,
            p_score=40,
            r_score=20,
            s_score=50,
            pattern_detected=False,
            recovery_time=5,
            gate_p=2,
            gate_r=2,
            gate_s=2,
            gate_d=2,
        )

        self.assertEqual(result["response"]["mode"], "SURVIVAL")

    def test_priority_engine_selects_correct_signal(self):
        module = DecisionSafetyModule()

        result = module.run(
            signals=[
                Signal(name="low_task", relevance=0.5, intensity=0.3, confidence=0.9),
                Signal(name="urgent_threat", relevance=0.9, intensity=0.9, confidence=0.9),
            ],
            detect=True,
            awareness=True,
            tension=0.2,
            regulation_possible=True,
            decision_possible=True,
            p_score=90,
            r_score=85,
            s_score=88,
            pattern_detected=False,
            recovery_time=1,
            gate_p=2,
            gate_r=2,
            gate_s=2,
            gate_d=2,
        )

        self.assertEqual(result["selected_signal"], "urgent_threat")

    def test_temporal_drop_triggers_adjustment(self):
        module = DecisionSafetyModule()

        result = module.run(
            signals=[Signal(name="task", relevance=0.8, intensity=0.5, confidence=0.9)],
            detect=True,
            awareness=True,
            tension=0.4,
            regulation_possible=True,
            decision_possible=True,
            p_score=80,
            r_score=60,
            s_score=70,
            pattern_detected=True,
            recovery_time=5,
            gate_p=2,
            gate_r=2,
            gate_s=2,
            gate_d=2,
        )

        self.assertTrue(result["temporal"]["preemptive_adjustment"])

    def test_survival_overrides_gate(self):
        module = DecisionSafetyModule(gate_threshold=1)

        result = module.run(
            signals=[Signal(name="threat", relevance=0.9, intensity=0.9, confidence=0.9)],
            detect=True,
            awareness=True,
            tension=0.95,
            regulation_possible=False,
            decision_possible=True,
            p_score=30,
            r_score=20,
            s_score=50,
            pattern_detected=False,
            recovery_time=5,
            gate_p=2,
            gate_r=2,
            gate_s=2,
            gate_d=2,
        )

        self.assertEqual(result["response"]["mode"], "SURVIVAL")
        self.assertNotEqual(result["response"]["action"], "ACT")

    def test_random_inputs_100_no_crash(self):
        random.seed(7)
        module = DecisionSafetyModule(gate_threshold=1)

        for i in range(100):
            signals = [
                Signal(
                    name=f"sig_{i}_{j}",
                    relevance=random.random(),
                    intensity=random.random(),
                    confidence=random.random(),
                )
                for j in range(random.randint(1, 5))
            ]
            result = module.run(
                signals=signals,
                detect=random.choice([True, False]),
                awareness=random.choice([True, False]),
                tension=random.random(),
                regulation_possible=random.choice([True, False]),
                decision_possible=random.choice([True, False]),
                p_score=random.randint(0, 100),
                r_score=random.randint(0, 100),
                s_score=random.randint(0, 100),
                pattern_detected=random.choice([True, False]),
                recovery_time=random.randint(0, 10),
                gate_p=random.randint(0, 3),
                gate_r=random.randint(0, 3),
                gate_s=random.randint(0, 3),
                gate_d=random.randint(0, 3),
            )

            self.assertTrue(("response" in result) or result.get("stopped", False))

    def test_invariants(self):
        module = DecisionSafetyModule(gate_threshold=1)

        for _ in range(50):
            result = module.run(
                signals=[Signal(name="x", relevance=0.9, intensity=0.9, confidence=0.9)],
                detect=True,
                awareness=True,
                tension=0.1,
                regulation_possible=True,
                decision_possible=True,
                p_score=90,
                r_score=90,
                s_score=90,
                pattern_detected=False,
                recovery_time=1,
                gate_p=2,
                gate_r=2,
                gate_s=2,
                gate_d=2,
            )

            if result.get("stopped") and result.get("response", {}).get("mode") != "SURVIVAL":
                self.assertNotIn("action", result.get("response", {}))

            if result.get("response", {}).get("mode") == "SURVIVAL":
                self.assertIn(result["response"]["action"], ["ACT", "DELAY", "IGNORE"])

    def test_determinism(self):
        module = DecisionSafetyModule(gate_threshold=1)

        params = dict(
            signals=[Signal(name="threat", relevance=0.9, intensity=0.9, confidence=0.9)],
            detect=True,
            awareness=True,
            tension=0.2,
            regulation_possible=True,
            decision_possible=True,
            p_score=90,
            r_score=90,
            s_score=90,
            pattern_detected=False,
            recovery_time=1,
            gate_p=2,
            gate_r=2,
            gate_s=2,
            gate_d=2,
        )

        r1 = module.run(**params)
        r2 = module.run(**params)
        self.assertEqual(r1, r2)

    def test_gate_monotonicity(self):
        m1 = DecisionSafetyModule(gate_threshold=1)
        m2 = DecisionSafetyModule(gate_threshold=2)

        params = dict(
            signals=[Signal(name="x", relevance=0.9, intensity=0.9, confidence=0.9)],
            detect=True,
            awareness=True,
            tension=0.2,
            regulation_possible=True,
            decision_possible=True,
            p_score=90,
            r_score=90,
            s_score=90,
            pattern_detected=False,
            recovery_time=1,
            gate_p=2,
            gate_r=2,
            gate_s=2,
            gate_d=2,
        )

        r1 = m1.run(**params)
        r2 = m2.run(**params)

        self.assertEqual(r1["gate"], GateAction.ALLOW.value)
        self.assertTrue(r2["stopped"] or r2.get("gate") != GateAction.ALLOW.value)

    def test_mode_hysteresis(self):
        module = DecisionSafetyModule(gate_threshold=1)
        common_params = dict(
            signals=[Signal(name="x", relevance=0.9, intensity=0.9, confidence=0.9)],
            detect=True,
            awareness=True,
            regulation_possible=True,
            decision_possible=True,
            p_score=90,
            r_score=90,
            s_score=90,
            pattern_detected=False,
            recovery_time=1,
            gate_p=2,
            gate_r=2,
            gate_s=2,
            gate_d=2,
        )
        r1 = module.run(tension=0.6, **common_params)
        r2 = module.run(tension=0.61, **common_params)
        self.assertEqual(r1["mode"], r2["mode"])

    def test_threshold_boundaries(self):
        module = DecisionSafetyModule(gate_threshold=1)
        result = module.run(
            signals=[Signal(name="x", relevance=0.9, intensity=0.9, confidence=0.9)],
            detect=True,
            awareness=True,
            tension=0.2,
            regulation_possible=True,
            decision_possible=True,
            p_score=90,
            r_score=90,
            s_score=90,
            pattern_detected=False,
            recovery_time=1,
            gate_p=1,
            gate_r=1,
            gate_s=1,
            gate_d=1,
        )

        self.assertEqual(result["gate"], GateAction.STOP.value)

    def test_performance(self):
        module = DecisionSafetyModule(gate_threshold=1)
        params = dict(
            signals=[Signal(name="x", relevance=0.9, intensity=0.9, confidence=0.9)],
            detect=True,
            awareness=True,
            tension=0.2,
            regulation_possible=True,
            decision_possible=True,
            p_score=90,
            r_score=90,
            s_score=90,
            pattern_detected=False,
            recovery_time=1,
            gate_p=2,
            gate_r=2,
            gate_s=2,
            gate_d=2,
        )

        start = time.time()
        for _ in range(1000):
            module.run(**params)
        self.assertLess(time.time() - start, 1.0)


if __name__ == "__main__":
    unittest.main()
