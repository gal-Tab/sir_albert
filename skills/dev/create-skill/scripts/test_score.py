import unittest, math
from score import scenario_pass_rate, skill_score, standard_error, lift, is_plateau, judge_agreement, is_borderline, build_report, format_report

class TestMetrics(unittest.TestCase):
    def test_pass_rate(self):
        self.assertEqual(scenario_pass_rate(2, 4), 0.5)
    def test_pass_rate_zero_k_raises(self):
        with self.assertRaises(ValueError):
            scenario_pass_rate(1, 0)
    def test_skill_score_is_mean(self):
        self.assertAlmostEqual(skill_score([0.0, 0.5, 1.0]), 0.5)
    def test_skill_score_empty_raises(self):
        with self.assertRaises(ValueError):
            skill_score([])
    def test_standard_error(self):
        self.assertAlmostEqual(standard_error(0.5, 4, 3), math.sqrt(0.25/12))
    def test_lift(self):
        self.assertAlmostEqual(lift(0.85, 0.40), 0.45)

class TestConvergence(unittest.TestCase):
    def test_plateau_true_when_deltas_below_se(self):
        # deltas 0.01, 0.01 both < se=0.05 -> plateau
        self.assertTrue(is_plateau([0.80, 0.81, 0.82], se=0.05))
    def test_plateau_false_when_still_improving(self):
        self.assertFalse(is_plateau([0.40, 0.60, 0.85], se=0.05))
    def test_plateau_false_when_too_short(self):
        self.assertFalse(is_plateau([0.80], se=0.05))
    def test_judge_agreement_unanimous(self):
        self.assertEqual(judge_agreement([1, 1, 1]), 1.0)
    def test_judge_agreement_split(self):
        self.assertAlmostEqual(judge_agreement([1, 0, 0]), 2/3)
    def test_judge_agreement_empty_raises(self):
        with self.assertRaises(ValueError):
            judge_agreement([])
    def test_borderline(self):
        self.assertTrue(is_borderline(0.5))
        self.assertFalse(is_borderline(0.85))

class TestReport(unittest.TestCase):
    def _data(self):
        return {
            "k": 3,
            "baseline": {"pass_rates": [0.33, 0.33]},
            "iterations": [
                {"pass_rates": [0.33, 0.67], "judges": [[1,0,0],[1,1,0]]},
                {"pass_rates": [1.0, 1.0],  "judges": [[1,1,1],[1,1,1]]},
            ],
        }
    def test_baseline_score(self):
        r = build_report(self._data())
        self.assertAlmostEqual(r["baseline_score"], 0.33)
    def test_lift_computed_vs_baseline(self):
        r = build_report(self._data())
        self.assertAlmostEqual(r["iterations"][-1]["lift"], 1.0 - 0.33, places=2)
    def test_stop_reason_present(self):
        r = build_report(self._data())
        self.assertIn(r["stop_reason"], {"threshold", "plateau", "budget", "in_progress"})
    def test_format_report_is_text(self):
        r = build_report(self._data())
        out = format_report(r)
        self.assertIsInstance(out, str)
        self.assertIn("baseline", out.lower())

if __name__ == "__main__":
    unittest.main()
