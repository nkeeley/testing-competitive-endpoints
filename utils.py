import time
import json
import os

RESULTS_RAW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "raw")


def timed_call(fn, *args, **kwargs):
    start = time.time()
    try:
        result = fn(*args, **kwargs)
        elapsed = time.time() - start
        return {"result": result, "latency_s": round(elapsed, 3), "error": None}
    except Exception as e:
        elapsed = time.time() - start
        return {"result": None, "latency_s": round(elapsed, 3), "error": str(e)}


def save_result(step_num, competitor_name, data):
    os.makedirs(RESULTS_RAW_DIR, exist_ok=True)
    slug = competitor_name.lower().replace(" ", "_")
    filepath = os.path.join(RESULTS_RAW_DIR, f"step{step_num}_{slug}.json")
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)
    return filepath


def excerpt(obj, n=500):
    if obj is None:
        return "(no content)"
    text = obj if isinstance(obj, str) else json.dumps(obj, default=str)
    if len(text) <= n:
        return text
    return text[:n] + f"\n... [{len(text) - n} more chars]"


def credits_used(result_dict):
    """Extract Firecrawl creditsUsed from a scrape/crawl/search response."""
    if not isinstance(result_dict, dict):
        return "not reported"
    for key in ("creditsUsed", "credits_used"):
        if key in result_dict:
            return result_dict[key]
    meta = result_dict.get("metadata") or result_dict.get("usage") or {}
    if isinstance(meta, dict):
        for key in ("creditsUsed", "credits_used"):
            if key in meta:
                return meta[key]
    return "not reported"


def print_step_header(step_num, step_name, target):
    bar = "=" * 60
    print(f"\n{bar}")
    print(f"=== STEP {step_num}: {step_name} — {target} ===")
    print(f"{bar}\n")


def print_competitor_header(name):
    print(f"\n--- {name} ---")


def print_comparison_table(competitors, rows):
    print("\n--- COMPARISON TABLE (fill in quality scores manually) ---\n")
    header = "| Dimension | " + " | ".join(competitors) + " |"
    sep = "|---|" + "---|" * len(competitors)
    print(header)
    print(sep)
    for label, values in rows:
        cells = " | ".join(str(values.get(c, "N/A")) for c in competitors)
        print(f"| {label} | {cells} |")
    print()
