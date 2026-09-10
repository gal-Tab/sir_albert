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
