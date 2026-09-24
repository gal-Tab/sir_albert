import json, sys, math

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

TARGET_LIFT = 0.4   # SHOULD default; override per skill
LOW_AGREE_THRESHOLD = 0.67  # judge-panel majority floor
MIN_SCENARIO_PASS = 0.67  # per-scenario reliability floor; encodes spec §5.3 "low cross-scenario variance"

def build_report(data, target_lift=TARGET_LIFT):
    k = data["k"]
    base = skill_score(data["baseline"]["pass_rates"])
    history = [base]
    iters = []
    stop_reason = "in_progress"
    for it in data["iterations"]:
        n = len(it["pass_rates"])
        score = skill_score(it["pass_rates"])
        se = standard_error(score, n, k)
        history.append(score)
        borderline = [i for i, pr in enumerate(it["pass_rates"]) if is_borderline(pr)]
        weak = [i for i, pr in enumerate(it["pass_rates"]) if pr < MIN_SCENARIO_PASS]
        low_agree = []
        for i, judges in enumerate(it.get("judges", [])):
            agree = judge_agreement(judges)
            if agree <= LOW_AGREE_THRESHOLD:
                low_agree.append(i)
        iters.append({
            "score": score,
            "lift": lift(score, base),
            "se": se,
            "plateau": is_plateau(history, se),
            "borderline_scenarios": borderline,
            "weak_scenarios": weak,
            "low_agreement_scenarios": low_agree,
        })
        if lift(score, base) >= target_lift and not weak:
            stop_reason = "threshold"
            break
        if iters[-1]["plateau"]:
            stop_reason = "plateau"
            break
    else:
        stop_reason = "budget"
    return {"baseline_score": base, "iterations": iters, "stop_reason": stop_reason}

def format_report(report):
    lines = [f"baseline score: {report['baseline_score']:.2f}"]
    for i, it in enumerate(report["iterations"]):
        lines.append(
            f"  iter {i}: score={it['score']:.2f} lift={it['lift']:+.2f} "
            f"se={it['se']:.3f} plateau={it['plateau']} "
            f"borderline={it['borderline_scenarios']} weak={it['weak_scenarios']} low_agreement={it['low_agreement_scenarios']}"
        )
    lines.append(f"stop: {report['stop_reason']}")
    return "\n".join(lines)

def main():
    data = json.load(sys.stdin)
    print(format_report(build_report(data)))

if __name__ == "__main__":
    main()
