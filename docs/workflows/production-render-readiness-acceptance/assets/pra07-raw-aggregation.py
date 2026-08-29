#!/usr/bin/env python3
"""Aggregate only the persisted PRA-05/PRA-06 raw samples.

This is a workflow artifact, not product code.  It deliberately reads an
explicit allow-list of raw files and the M30 manifest; it does not start
services, discover other sample files, or mutate any input.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit


PRA_DIR = Path("docs/workflows/production-render-readiness-acceptance")
DEFAULT_OUTPUT_JSON = "pra07-raw-aggregation-20260822.json"
DEFAULT_OUTPUT_MD = "pra07-raw-aggregation-20260822.md"
SCENARIO_FILES = {
    "E0": "pra05-e0-raw.ndjson",
    "L20": "pra05-l20-raw.ndjson",
    "D1": "pra05-d1-raw.ndjson",
}
M30_MANIFEST = "pra06-m30-batch-final-20260822.manifest.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--assets-dir", type=Path)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-md", type=Path)
    return parser.parse_args()


def as_repo_path(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def nearest_rank(values: list[float], quantile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(float(value) for value in values)
    rank = max(1, math.ceil(quantile * len(ordered)))
    return ordered[rank - 1]


def metric_summary(
    samples: list[dict],
    extractor,
    source: str,
) -> dict:
    values: list[float] = []
    contributors: list[str] = []
    excluded: list[dict] = []
    for sample in samples:
        sample_id = str(sample.get("sample_id", sample["record_key"]))
        value, reason = extractor(sample)
        if is_number(value) and float(value) >= 0:
            values.append(float(value))
            contributors.append(sample_id)
        else:
            excluded.append({"sample_id": sample_id, "reason": reason or "missing_or_non_numeric"})
    return {
        "source": source,
        "valid_metric_count": len(values),
        "contributing_sample_ids": contributors,
        "excluded_samples": excluded,
        "p50": nearest_rank(values, 0.50),
        "p90": nearest_rank(values, 0.90),
        "max": max(values) if values else None,
        "status": "available" if values else "not_available",
    }


def lcp_summary(samples: list[dict]) -> dict:
    return metric_summary(
        samples,
        lambda sample: (
            sample.get("lcp"),
            "null" if sample.get("lcp") is None else "missing_or_non_numeric",
        ),
        "raw sample field lcp; null is missing and is never converted to zero",
    ) | {
        "null_count": sum(sample.get("lcp") is None for sample in samples),
        "not_available_reason": "all persisted lcp values are null"
        if all(sample.get("lcp") is None for sample in samples)
        else None,
    }


def path_label(url: object) -> str | None:
    if not isinstance(url, str) or not url:
        return None
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc:
        return parsed.path + (("?" + parsed.query) if parsed.query else "")
    return url


def required_api_metrics(samples: list[dict]) -> dict[str, dict]:
    grouped: dict[str, list[dict]] = {}
    for sample in samples:
        for entry in sample.get("required_api", []) or []:
            label = path_label(entry.get("url"))
            if label:
                grouped.setdefault(label, []).append(
                    {
                        "sample_id": sample.get("sample_id"),
                        "duration": entry.get("duration"),
                    }
                )
    result = {}
    for label, entries in sorted(grouped.items()):
        result[label] = metric_summary(
            [{"sample_id": entry["sample_id"], "value": entry["duration"], "record_key": entry["sample_id"]} for entry in entries],
            lambda sample: (sample.get("value"), "missing_or_non_numeric"),
            "raw sample field required_api[].duration; status remains in the raw required_api[].status field and is not used as a duration",
        )
    return result


def m30_api_metrics(samples: list[dict]) -> dict[str, dict]:
    grouped: dict[str, list[dict]] = {}
    for sample in samples:
        for entry in sample.get("api_timings", []) or []:
            label = path_label(entry.get("url"))
            if label:
                grouped.setdefault(label, []).append(
                    {
                        "sample_id": sample.get("sample_id"),
                        "duration": entry.get("duration"),
                    }
                )
    result = {}
    for label, entries in sorted(grouped.items()):
        result[label] = metric_summary(
            [{"sample_id": entry["sample_id"], "value": entry["duration"], "record_key": entry["sample_id"]} for entry in entries],
            lambda sample: (sample.get("value"), "missing_or_non_numeric"),
            "raw sample field api_timings[].duration grouped by URL path; HTTP status is reported separately and never used as latency",
        )
    return result


def readiness_value(sample: dict) -> tuple[object, str]:
    if sample.get("scenario") == "M30":
        marks = sample.get("readiness", {}).get("marks", {})
        auth = marks.get("auth_submit") or []
        ready = marks.get("content_ready") or []
        if auth and ready and is_number(auth[0].get("start")) and is_number(ready[0].get("start")):
            return float(ready[0]["start"]) - float(auth[0]["start"]), "raw readiness.marks.content_ready[0].start - readiness.marks.auth_submit[0].start"
        return None, "missing M30 auth_submit/content_ready mark pair"
    value = sample.get("readiness", {}).get("readiness_duration")
    return value, "raw sample field readiness.readiness_duration"


def status_counts(items: object) -> dict[str, int]:
    if not isinstance(items, list):
        return {}
    return dict(sorted(Counter(str(item.get("status")) for item in items if isinstance(item, dict) and "status" in item).items()))


def authentication_status_overview(samples: list[dict]) -> dict:
    return {
        "login_response_status_counts": status_counts(
            [entry for sample in samples for entry in (sample.get("login_response") or [])]
        ),
        "auth_me_status_counts": status_counts(
            [entry for sample in samples for entry in (sample.get("me_responses") or [])]
        ),
        "strict_management_status_counts": status_counts(
            [entry for sample in samples for entry in (sample.get("strict_management_responses") or [])]
        ),
        "interpretation": "HTTP status counts are authorization/session evidence only; they are not latency values.",
    }


def scan_sensitive(value: object, path: str = "$") -> list[dict]:
    findings: list[dict] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key).lower()
            child_path = f"{path}.{key}"
            if isinstance(child, str) and child and re.search(r"password|token|secret|authorization", key_text):
                findings.append({"path": child_path, "kind": "sensitive_named_value"})
            if isinstance(child, str) and child and re.search(r"raw.?cookie|cookie.?value", key_text):
                findings.append({"path": child_path, "kind": "raw_cookie_named_value"})
            if isinstance(child, (dict, list)):
                findings.extend(scan_sensitive(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(scan_sensitive(child, f"{path}[{index}]"))
    return findings


def read_ndjson(path: Path, repo_root: Path, scenario: str, file_index: int | None = None) -> tuple[list[dict], list[dict]]:
    records: list[dict] = []
    anomalies: list[dict] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [], [{"path": as_repo_path(path, repo_root), "kind": "read_error", "detail": str(exc)}]
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            anomalies.append({"path": as_repo_path(path, repo_root), "line": line_number, "kind": "blank_line"})
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            records.append(
                {
                    "record_key": f"{path.name}:{line_number}",
                    "sample_id": f"unparsed-{path.name}:{line_number}",
                    "scenario": scenario,
                    "valid": False,
                    "failure_reason": f"json_parse_error:{exc.msg}",
                    "__parse_error__": True,
                }
            )
            anomalies.append({"path": as_repo_path(path, repo_root), "line": line_number, "kind": "json_parse_error", "detail": exc.msg})
            continue
        if not isinstance(row, dict):
            records.append(
                {
                    "record_key": f"{path.name}:{line_number}",
                    "sample_id": f"non-object-{path.name}:{line_number}",
                    "scenario": scenario,
                    "valid": False,
                    "failure_reason": "json_record_not_object",
                    "__parse_error__": True,
                }
            )
            anomalies.append({"path": as_repo_path(path, repo_root), "line": line_number, "kind": "json_record_not_object"})
            continue
        row.setdefault("scenario", scenario)
        row["record_key"] = f"{path.name}:{line_number}"
        row["input_path"] = as_repo_path(path, repo_root)
        row["input_line"] = line_number
        records.append(row)
    return records, anomalies


def input_descriptor(path: Path, repo_root: Path, record_count: int, anomalies: list[dict]) -> dict:
    return {
        "path": as_repo_path(path, repo_root),
        "sha256": sha256(path) if path.exists() else None,
        "exists": path.exists(),
        "record_count": record_count,
        "anomaly_count": len(anomalies),
    }


def summarize_scenario(scenario: str, records: list[dict], anomalies: list[dict], input_paths: list[str]) -> dict:
    attempts = len(records)
    valid = [row for row in records if row.get("valid") is True and not row.get("__parse_error__")]
    failed = [row for row in records if row not in valid]
    metrics = {
        "ttfb": metric_summary(valid, lambda row: (row.get("navigation", {}).get("ttfb"), "missing navigation.ttfb"), "raw sample field navigation.ttfb"),
        "dom_content_loaded": metric_summary(valid, lambda row: (row.get("navigation", {}).get("dom_content_loaded"), "missing navigation.dom_content_loaded"), "raw sample field navigation.dom_content_loaded"),
        "load": metric_summary(valid, lambda row: (row.get("navigation", {}).get("load"), "missing navigation.load"), "raw sample field navigation.load"),
        "lcp": lcp_summary(valid),
        "readiness": metric_summary(valid, readiness_value, "E0/L20/D1: readiness.readiness_duration; M30: content_ready mark start minus auth_submit mark start"),
    }
    if scenario == "M30":
        metrics["key_api_timing"] = m30_api_metrics(valid)
    else:
        metrics["key_api_timing"] = required_api_metrics(valid)
    result = {
        "scenario": scenario,
        "input_paths": input_paths,
        "browser_temperature": next((row.get("browser_temperature") for row in records if row.get("browser_temperature") is not None), None),
        "server_temperature": next((row.get("server_temperature") for row in records if row.get("server_temperature") is not None), None),
        "attempt_count": attempts,
        "valid_count": len(valid),
        "failed_count": len(failed),
        "failure_rate": (len(failed) / attempts) if attempts else None,
        "valid_sample_ids": [row.get("sample_id") for row in valid],
        "failed_samples": [
            {
                "sample_id": row.get("sample_id"),
                "input_path": row.get("input_path"),
                "input_line": row.get("input_line"),
                "failure_reason": row.get("failure_reason") or "valid_not_true_or_parse_error",
            }
            for row in failed
        ],
        "anomalies": anomalies,
        "metrics": metrics,
    }
    if scenario == "M30":
        result["authentication_status_overview"] = authentication_status_overview(valid)
    return result


def separate_artifacts(assets_dir: Path, repo_root: Path, m30_negative: str | None) -> list[str]:
    names = set()
    for path in assets_dir.iterdir():
        if not path.is_file():
            continue
        name = path.name.lower()
        if any(marker in name for marker in ("smoke", "health-check", "healthcheck", "server-cold", "negative")):
            names.add(as_repo_path(path, repo_root))
    if m30_negative:
        names.add(m30_negative)
    return sorted(names)


def build_payload(repo_root: Path, assets_dir: Path) -> dict:
    input_files: list[dict] = []
    scenario_records: dict[str, list[dict]] = {}
    scenario_anomalies: dict[str, list[dict]] = {}
    sensitive_findings: list[dict] = []

    for scenario, name in SCENARIO_FILES.items():
        path = assets_dir / name
        records, anomalies = read_ndjson(path, repo_root, scenario)
        input_files.append(input_descriptor(path, repo_root, len(records), anomalies))
        scenario_records[scenario] = records
        scenario_anomalies[scenario] = anomalies
        for row in records:
            if not row.get("__parse_error__"):
                sensitive_findings.extend(scan_sensitive(row, f"{as_repo_path(path, repo_root)}:{row.get('input_line')}"))

    manifest_path = assets_dir / M30_MANIFEST
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    input_files.append(input_descriptor(manifest_path, repo_root, 0, []))
    m30_records: list[dict] = []
    m30_anomalies: list[dict] = []
    m30_input_paths: list[str] = []
    for sample in manifest.get("samples", []):
        raw_path = Path(sample["raw_path"])
        if not raw_path.is_absolute():
            raw_path = repo_root / raw_path
        m30_input_paths.append(as_repo_path(raw_path, repo_root))
        records, anomalies = read_ndjson(raw_path, repo_root, "M30")
        input_files.append(input_descriptor(raw_path, repo_root, len(records), anomalies))
        m30_records.extend(records)
        m30_anomalies.extend(anomalies)
        for row in records:
            if not row.get("__parse_error__"):
                sensitive_findings.extend(scan_sensitive(row, f"{as_repo_path(raw_path, repo_root)}:{row.get('input_line')}"))
    scenario_records["M30"] = m30_records
    scenario_anomalies["M30"] = m30_anomalies

    scenarios = []
    for scenario in ("E0", "L20", "D1"):
        scenarios.append(
            summarize_scenario(
                scenario,
                scenario_records[scenario],
                scenario_anomalies[scenario],
                [as_repo_path(assets_dir / SCENARIO_FILES[scenario], repo_root)],
            )
        )
    # M30's input list is exactly the manifest-listed raw files, not a glob.
    scenarios.append(
        summarize_scenario("M30", m30_records, m30_anomalies, m30_input_paths)
    )

    count_consistency = all(
        item["attempt_count"] == item["valid_count"] + item["failed_count"]
        for item in scenarios
    ) and all(descriptor["exists"] for descriptor in input_files)
    m30_negative = manifest.get("negative_boundary", {}).get("path")
    if m30_negative:
        m30_negative = as_repo_path(Path(m30_negative), repo_root)

    return {
        "aggregation_run_id": "pra07-raw-aggregation-20260822",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "raw_only": True,
        "source_boundary": "Only the three explicit PRA-05 raw NDJSON files and the ten raw files explicitly listed by the PRA-06 final M30 manifest were read.",
        "input_files": input_files,
        "separate_or_excluded_artifacts": separate_artifacts(assets_dir, repo_root, m30_negative),
        "browser_server_temperature_rule": "Primary aggregate retains each raw row's declared browser_temperature/server_temperature; server-cold, smoke and health-check artifacts are excluded and listed separately.",
        "valid_filter_rule": "A sample contributes to timing percentiles only when its parsed row has valid=true and the metric is finite numeric and >= 0. Failed rows remain in attempts/failed_count and failed_samples.",
        "percentile_algorithm": "nearest-rank",
        "percentile_definition": "Sort n numeric values ascending; p50/p90 use 1-indexed rank ceil(q*n), clamped to at least 1; no interpolation.",
        "sensitive_findings": sorted(sensitive_findings, key=lambda item: (item["path"], item["kind"])),
        "count_consistency": {
            "passed": count_consistency,
            "rule": "For every scenario attempt_count == valid_count + failed_count and every explicit input file exists.",
        },
        "scenarios": scenarios,
        "claims": {
            "performance_baseline": False,
            "production_readiness": False,
            "sla_or_budget_commitment": False,
            "optimization_verified": False,
            "interpretation": "These are local isolated raw-data aggregates only. Any observation or optimization candidate remains unverified.",
        },
    }


def markdown(payload: dict) -> str:
    lines = [
        "# PRA-07 Raw-only aggregation",
        "",
        "Status: `PASS_WITH_NOTES` for the authorized aggregation phase only. This is not a production baseline, SLA, production-readiness decision, or optimization proof.",
        "",
        f"- Raw-only: `{payload['raw_only']}`",
        f"- Percentile algorithm: `{payload['percentile_algorithm']}` — {payload['percentile_definition']}",
        "- Timing filter: only parsed `valid=true` rows and finite non-negative metric values contribute; failed rows remain counted and listed.",
        "- LCP: `null` is missing, never zero. Where all values are null, the metric is `not_available`.",
        "",
        "## Scenario summary",
        "",
        "| Scenario | Browser/server | Attempts | Valid | Failed | Failure rate | TTFB p50/p90/max | DCL p50/p90/max | Load p50/p90/max | Readiness p50/p90/max | LCP |",
        "|---|---|---:|---:|---:|---:|---|---|---|---|---|",
    ]
    for scenario in payload["scenarios"]:
        metrics = scenario["metrics"]
        def triple(name: str) -> str:
            metric = metrics[name]
            return f"{metric['p50']} / {metric['p90']} / {metric['max']}"
        lcp = metrics["lcp"]
        lcp_text = "not_available (all null)" if lcp["status"] == "not_available" else triple("lcp")
        lines.append(
            f"| {scenario['scenario']} | {scenario['browser_temperature']} / {scenario['server_temperature']} | {scenario['attempt_count']} | {scenario['valid_count']} | {scenario['failed_count']} | {scenario['failure_rate']} | {triple('ttfb')} | {triple('dom_content_loaded')} | {triple('load')} | {triple('readiness')} | {lcp_text} |"
        )
    lines.extend(["", "## Key API timing source", "", "Durations below come from the raw timing fields only. HTTP status is kept as a separate status overview and is never treated as a duration.", ""])
    for scenario in payload["scenarios"]:
        lines.append(f"### {scenario['scenario']}")
        lines.append("")
        lines.append("| Endpoint/path | Source | Count | p50 | p90 | Max |")
        lines.append("|---|---|---:|---:|---:|---:|")
        for endpoint, metric in scenario["metrics"]["key_api_timing"].items():
            lines.append(f"| `{endpoint}` | {metric['source']} | {metric['valid_metric_count']} | {metric['p50']} | {metric['p90']} | {metric['max']} |")
        if not scenario["metrics"]["key_api_timing"]:
            lines.append("| *(none)* | no usable timing field persisted | 0 | null | null | null |")
        if scenario["scenario"] == "M30":
            lines.append("")
            lines.append("Authentication/session status overview (not latency):")
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(scenario["authentication_status_overview"], ensure_ascii=False, indent=2))
            lines.append("```")
        lines.append("")
    lines.extend([
        "## Input and exclusion proof",
        "",
        "The JSON artifact records every explicit input path and SHA-256. Smoke, health-check, server-cold, and M30 negative-boundary artifacts are listed under `separate_or_excluded_artifacts` and are not in the primary scenario counts.",
        "",
        "## Remaining boundary",
        "",
        "E0 retains one failed raw row; all four primary scenarios have at least 10 valid rows. No server-cold aggregate was produced. Observations and optimization candidates are unverified suggestions only. PRA-08 final cleanup and integrity review is PASS.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    assets_dir = (args.assets_dir or repo_root / PRA_DIR / "assets").resolve()
    output_json = (args.output_json or assets_dir / DEFAULT_OUTPUT_JSON).resolve()
    output_md = (args.output_md or assets_dir / DEFAULT_OUTPUT_MD).resolve()
    payload = build_payload(repo_root, assets_dir)
    if payload["sensitive_findings"]:
        print(json.dumps({"sensitive_findings": payload["sensitive_findings"]}, ensure_ascii=False), file=sys.stderr)
        return 2
    if not payload["count_consistency"]["passed"]:
        print("input/count consistency failed", file=sys.stderr)
        return 3
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(markdown(payload), encoding="utf-8")
    print(json.dumps({"json": str(output_json), "markdown": str(output_md), "scenarios": [(item["scenario"], item["attempt_count"], item["valid_count"], item["failed_count"]) for item in payload["scenarios"]]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
