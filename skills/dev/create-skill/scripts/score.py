import math

def scenario_pass_rate(passes, k):
    if k <= 0:
        raise ValueError("k must be > 0")
    return passes / k

def skill_score(pass_rates):
    if not pass_rates:
        raise ValueError("no scenarios")
    return sum(pass_rates) / len(pass_rates)

def standard_error(p, n, k):
    if n <= 0 or k <= 0:
        raise ValueError("n and k must be > 0")
    return math.sqrt(p * (1 - p) / (n * k))

def lift(candidate, baseline):
    return candidate - baseline

def is_plateau(history, se, patience=2, factor=1.0):
    if len(history) < patience + 1:
        return False
    recent = history[-(patience + 1):]
    deltas = [abs(recent[i + 1] - recent[i]) for i in range(len(recent) - 1)]
    return all(d < factor * se for d in deltas)

def judge_agreement(judge_scores):
    if not judge_scores:
        raise ValueError("no judges")
    frac_pass = sum(1 for s in judge_scores if s >= 0.5) / len(judge_scores)
    return max(frac_pass, 1 - frac_pass)

def is_borderline(score, low=0.4, high=0.6):
    return low <= score <= high
