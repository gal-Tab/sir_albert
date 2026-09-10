import unittest, math
from score import scenario_pass_rate, skill_score, standard_error, lift

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

if __name__ == "__main__":
    unittest.main()
