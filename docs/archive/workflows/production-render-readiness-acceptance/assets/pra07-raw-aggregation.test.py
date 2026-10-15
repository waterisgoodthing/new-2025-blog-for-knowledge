#!/usr/bin/env python3
"""Small CLI contract test for the PRA-07 raw-only aggregation asset."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SCRIPT = Path(__file__).with_name("pra07-raw-aggregation.py")
ASSETS = SCRIPT.parent


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="pra07-aggregation-test-") as tmp:
        output_json = Path(tmp) / "aggregation.json"
        output_md = Path(tmp) / "aggregation.md"
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--repo-root",
                str(ROOT),
                "--assets-dir",
                str(ASSETS),
                "--output-json",
                str(output_json),
                "--output-md",
                str(output_md),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise AssertionError(
                f"aggregation CLI failed: rc={result.returncode}\n"
                f"stdout={result.stdout}\nstderr={result.stderr}"
            )
        payload = json.loads(output_json.read_text(encoding="utf-8"))
        assert payload["raw_only"] is True
        assert payload["percentile_algorithm"] == "nearest-rank"
        assert payload["sensitive_findings"] == []
        scenarios = {item["scenario"]: item for item in payload["scenarios"]}
        assert scenarios["E0"]["attempt_count"] == 11
        assert scenarios["E0"]["valid_count"] == 10
        assert scenarios["E0"]["failed_count"] == 1
        assert scenarios["L20"]["valid_count"] == 10
        assert scenarios["D1"]["valid_count"] == 10
        assert scenarios["M30"]["attempt_count"] == 10
        assert scenarios["M30"]["valid_count"] == 10
        assert scenarios["M30"]["authentication_status_overview"]
        for item in scenarios.values():
            assert item["failure_rate"] == item["failed_count"] / item["attempt_count"]
            assert item["metrics"]["lcp"]["status"] == "not_available"
            assert item["metrics"]["lcp"]["p50"] is None
            assert item["metrics"]["lcp"]["p90"] is None
            assert item["metrics"]["lcp"]["max"] is None
        excluded = payload["separate_or_excluded_artifacts"]
        assert any(path.endswith("/pra05-e0-smoke.ndjson") for path in excluded)
        assert any(path.endswith("/pra05-l20-health-check.ndjson") for path in excluded)
        assert output_md.read_text(encoding="utf-8").startswith("# PRA-07 Raw-only aggregation")
    print("pra07 raw aggregation contract: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
