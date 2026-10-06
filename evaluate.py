

import argparse
import json
import math
import statistics
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from Search_engin import verify_quote

TEST_SET = Path("Database") / "test_set.json"
REPORT_DIR = Path("reports")
ACCEPTED = ("matched", "matched_with_diff")



def wilson(k: int, n: int, z: float = 1.96):

    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half) * 100, min(1.0, centre + half) * 100)


def rate(k: int, n: int) -> str:
    if n == 0:
        return "n/a (0 cases)"
    lo, hi = wilson(k, n)
    return f"{100 * k / n:5.1f}%  ({k}/{n})  95% CI {lo:.0f}-{hi:.0f}%"



def outcome_of(case: dict, result: dict) -> str:
    exp_status = case["expected_status"]
    exp_source = case["expected_source"]
    status = result["status"]
    source = result.get("source_type") or "none"
    
    if exp_status == "too_short":
        return "guard_ok" if status == "too_short" else "guard_failed"

    if exp_status == "no_reference":
        return "rejected" if status == "no_reference" else "FALSE_ACCEPT"

    if exp_status == "matched":
        if status == "matched" and source == exp_source:
            return "correct"
        if status == "matched_with_diff" and source == exp_source:
            return "downgraded"
        if status == "no_reference":
            return "missed"
        return "wrong_source"

    if exp_status == "matched_with_diff":
        if status == "matched_with_diff":
            return "detected"
        if status == "matched":
            return "FALSE_ACCEPT"
        return "safe_miss"
    return "unknown"

 

def reference_ok(case: dict, result: dict):
    origin = case.get("origin")
    best = result.get("best_match")
    if not origin or not best or result["status"] not in ACCEPTED:
        return None
    if origin["source"] == "quran":
        return (best.get("surah_number") == origin["surah"]
                and best.get("ayah_number") == origin["ayah"])
    return (best.get("source_book") == origin["book"]
            and str(best.get("hadith_number")) == str(origin["number"]))


# Run + report
def run(cases: list, threshold: int) -> list:
    rows = []
    print(f"\nRunning {len(cases)} cases at threshold {threshold} ...", flush=True)
    for i, case in enumerate(cases, 1):
        t0 = time.perf_counter()
        result = verify_quote(case["text"], threshold=threshold)
        dt = time.perf_counter() - t0
        rows.append({"case": case, "result": result,
                     "outcome": outcome_of(case, result),
                     "ref_ok": reference_ok(case, result), "seconds": dt})
        if i % 10 == 0 or i == len(cases):
            print(f"  ... {i}/{len(cases)} cases", flush=True)
    return rows


def summarize(rows: list, threshold: int, split: str) -> dict:
    oc = [r["outcome"] for r in rows]
    exp = lambda r: r["case"]["expected_status"]
    src = lambda r: r["case"]["expected_source"]

    fabricated = [r for r in rows if exp(r) == "no_reference"]
    tampered = [r for r in rows if exp(r) == "matched_with_diff"]
    correct = [r for r in rows if exp(r) == "matched"]
    guard = [r for r in rows if exp(r) == "too_short"]

    false_accept = sum(1 for r in rows if r["outcome"] == "FALSE_ACCEPT")
    non_exact = len(fabricated) + len(tampered)

    def count(rs, label):
        return sum(1 for r in rs if r["outcome"] == label)

    q_correct = [r for r in correct if src(r) == "quran"]
    h_correct = [r for r in correct if src(r) == "hadith"]
    q_tamp = [r for r in tampered if src(r) == "quran"]
    h_tamp = [r for r in tampered if src(r) == "hadith"]

    exact_passed = sum(1 for r in tampered if r["outcome"] == "FALSE_ACCEPT")
    fab_accepted = sum(1 for r in fabricated if r["outcome"] == "FALSE_ACCEPT")

    ref_pool = [r for r in rows if r["ref_ok"] is not None]
    secs = sorted(r["seconds"] for r in rows)
    p95 = secs[min(len(secs) - 1, int(0.95 * len(secs)))] if secs else 0

    by_cat = defaultdict(Counter)
    for r in rows:
        by_cat[r["case"]["type"]][r["outcome"]] += 1

    return {
        "threshold": threshold, "split": split, "n_cases": len(rows),
        "far": (false_accept, non_exact),
        "tampered_as_exact": (exact_passed, len(tampered)),
        "fabricated_accepted": (fab_accepted, len(fabricated)),
        "quran_recognised": (count(q_correct, "correct"), len(q_correct)),
        "hadith_recognised": (count(h_correct, "correct"), len(h_correct)),
        "tampered_detected": (count(tampered, "detected"), len(tampered)),
        "tampered_detected_quran": (count(q_tamp, "detected"), len(q_tamp)),
        "tampered_detected_hadith": (count(h_tamp, "detected"), len(h_tamp)),
        "tampered_safe_miss": (count(tampered, "safe_miss"), len(tampered)),
        "abstention": (count(fabricated, "rejected"), len(fabricated)),
        "guard": (count(guard, "guard_ok"), len(guard)),
        "source_accuracy": (sum(1 for r in rows if (r["result"].get("source_type") or "none")
                                == src(r)), len(rows)),
        "reference_ok": (sum(1 for r in ref_pool if r["ref_ok"]), len(ref_pool)),
        "latency": {"mean": statistics.mean(secs) if secs else 0,
                    "median": statistics.median(secs) if secs else 0,
                    "p95": p95, "max": max(secs) if secs else 0},
        "by_category": {k: dict(v) for k, v in by_cat.items()},
    }


def print_report(m: dict, rows: list, details: bool):
    line = "=" * 78
    print(f"\n{line}\n EVALUATION REPORT | split = {m['split']} | threshold = {m['threshold']}"
          f" | {m['n_cases']} cases\n{line}")
    print(f" False-acceptance rate (FAR)    : {rate(*m['far'])}   <- lower is better")
    print(f"   tampered returned as exact   : {rate(*m['tampered_as_exact'])}")
    print(f"   not-in-books accepted        : {rate(*m['fabricated_accepted'])}")
    print(f" Correct quotes recognised      : Quran  {rate(*m['quran_recognised'])}")
    print(f"                                  Hadith {rate(*m['hadith_recognised'])}")
    print(f" Tampered quotes detected       : all    {rate(*m['tampered_detected'])}")
    print(f"                                  Quran  {rate(*m['tampered_detected_quran'])}")
    print(f"                                  Hadith {rate(*m['tampered_detected_hadith'])}")
    print(f" Tampered but safely refused    : {rate(*m['tampered_safe_miss'])}")
    print(f" Abstention (not in books)      : {rate(*m['abstention'])}")
    print(f" Too-short input guard          : {rate(*m['guard'])}")
    print(f" Source (Quran/Hadith) accuracy : {rate(*m['source_accuracy'])}")
    print(f" Returned reference == origin   : {rate(*m['reference_ok'])}   (informational)")
    lat = m["latency"]
    print(f" Latency per query              : mean {lat['mean']:.2f}s | median "
          f"{lat['median']:.2f}s | p95 {lat['p95']:.2f}s | max {lat['max']:.2f}s")

    print("\n By category (outcome counts):")
    for ctype, counts in m["by_category"].items():
        text = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
        print(f"   {ctype:22} {text}")

    good = {"correct", "detected", "rejected", "guard_ok"}
    bad = [r for r in rows if r["outcome"] not in good]
    print(f"\n Cases not handled as expected ({len(bad)}):")
    if details:
        for r in bad:
            c, res = r["case"], r["result"]
            best = res.get("best_match") or {}
            print(f"   #{c['id']:<3} {c['type']:<20} outcome={r['outcome']:<12} "
                  f"expected={c['expected_status']}/{c['expected_source']} "
                  f"got={res['status']}/{res.get('source_type')} "
                  f"score={best.get('score')} cov={best.get('coverage')}")
            print(f"        {c['text'][:90]}")
    else:
        print("   (re-run with --details to list them)")

    slow = sorted(rows, key=lambda r: r["seconds"], reverse=True)[:3]
    print("\n Slowest cases: " + " | ".join(
        f"#{r['case']['id']} {r['case']['type']} {r['seconds']:.2f}s" for r in slow))
    print(line)


def print_markdown(m: dict):
    def row(name, pair):
        k, n = pair
        if n == 0:
            return f"| {name} | n/a |"
        lo, hi = wilson(k, n)
        return f"| {name} | {100 * k / n:.1f}% ({k}/{n}), 95% CI {lo:.0f}-{hi:.0f}% |"

    print(f"\nBenchmark: {m['n_cases']} generated cases, split={m['split']}, "
          f"threshold {m['threshold']}. Small set: one case moves a rate by several points.\n")
    print("| Metric | Result |\n|---|---|")
    print(row("False-acceptance rate (FAR)", m["far"]))
    print(row("Correct Quran quotes recognised", m["quran_recognised"]))
    print(row("Correct Hadith quotes recognised", m["hadith_recognised"]))
    print(row("Tampered quotes detected (`matched_with_diff`)", m["tampered_detected"]))
    print(row("Tampered quotes safely refused (`no_reference`)", m["tampered_safe_miss"]))
    print(row("Text not in the books correctly refused", m["abstention"]))
    print(row("Too-short input guard", m["guard"]))
    lat = m["latency"]
    print(f"| Latency per query (mean / p95) | {lat['mean']:.2f}s / {lat['p95']:.2f}s |")


def main():
    ap = argparse.ArgumentParser(description="Evaluate Sanad on the generated test set.")
    ap.add_argument("-t", "--thresholds", type=int, nargs="+", default=[85])
    ap.add_argument("--split", choices=["tune", "test", "all"], default="tune")
    ap.add_argument("--types", nargs="+", help="only these categories")
    ap.add_argument("--details", action="store_true")
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--no-save", action="store_true")
    ap.add_argument("--max-far", type=float, default=None)
    ap.add_argument("--final", action="store_true",
                    help="required for --split test: logs the result in reports/final_test_log.json")
    args = ap.parse_args()

    if args.split in ("test", "all") and not args.final:
        sys.exit("Refusing: the test split is for the FINAL run only. Add --final "
                 "(one frozen threshold) if you really mean it.")
    if args.final and len(args.thresholds) != 1:
        sys.exit("--final needs exactly one (already frozen) threshold.")

    cases = json.load(open(TEST_SET, encoding="utf-8"))
    if args.split != "all":
        cases = [c for c in cases if c.get("split") == args.split]
    if args.types:
        cases = [c for c in cases if c["type"] in args.types]
    if not cases:
        sys.exit("No cases selected.")

    worst_far = 0.0
    for th in args.thresholds:
        rows = run(cases, th)
        m = summarize(rows, th, args.split)
        print_report(m, rows, args.details)
        if args.markdown:
            print_markdown(m)
        k, n = m["far"]
        worst_far = max(worst_far, 100 * k / n if n else 0)

        if not args.no_save:
            REPORT_DIR.mkdir(exist_ok=True)
            out = REPORT_DIR / f"eval_{args.split}_th{th}.json"
            json.dump(m, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
            print(f" saved -> {out}")
        if args.final:
            REPORT_DIR.mkdir(exist_ok=True)
            log = REPORT_DIR / "final_test_log.json"
            history = json.load(open(log, encoding="utf-8")) if log.exists() else []
            history.append({"time": datetime.now().isoformat(timespec="seconds"), **m})
            json.dump(history, open(log, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
            print(f" appended -> {log}  (runs so far: {len(history)})")

    if args.max_far is not None and worst_far > args.max_far:
        print(f"FAR {worst_far:.1f}% > allowed {args.max_far}%")
        sys.exit(1)


if __name__ == "__main__":
    main()