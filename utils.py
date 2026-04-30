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
    """Extract Firecrawl creditsUsed from a scrape/crawl/search response.
    Handles dict, Pydantic model, and string-serialized Pydantic (when saved JSON)."""
    if result_dict is None:
        return "not reported"
    # Pydantic model — try attribute access
    for attr in ("credits_used", "creditsUsed"):
        val = getattr(result_dict, attr, None)
        if val is not None:
            return val
    # Pydantic metadata
    meta = getattr(result_dict, "metadata", None) or getattr(result_dict, "usage", None)
    if meta is not None:
        for attr in ("credits_used", "creditsUsed"):
            val = getattr(meta, attr, None)
            if val is not None:
                return val
    # Dict path
    if isinstance(result_dict, dict):
        for key in ("creditsUsed", "credits_used"):
            if key in result_dict:
                return result_dict[key]
        meta = result_dict.get("metadata") or result_dict.get("usage") or {}
        if isinstance(meta, dict):
            for key in ("creditsUsed", "credits_used"):
                if key in meta:
                    return meta[key]
    # Last resort: string-search a serialized Pydantic dump
    try:
        import re
        s = str(result_dict)
        m = re.search(r"credits_used=(\d+)", s) or re.search(r"creditsUsed[\"':\s=]+(\d+)", s)
        if m:
            return int(m.group(1))
    except Exception:
        pass
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
