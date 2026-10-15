# PRA-07 Raw-only aggregation

Status: `PASS_WITH_NOTES` for the authorized aggregation phase only. This is not a production baseline, SLA, production-readiness decision, or optimization proof.

- Raw-only: `True`
- Percentile algorithm: `nearest-rank` — Sort n numeric values ascending; p50/p90 use 1-indexed rank ceil(q*n), clamped to at least 1; no interpolation.
- Timing filter: only parsed `valid=true` rows and finite non-negative metric values contribute; failed rows remain counted and listed.
- LCP: `null` is missing, never zero. Where all values are null, the metric is `not_available`.

## Scenario summary

| Scenario | Browser/server | Attempts | Valid | Failed | Failure rate | TTFB p50/p90/max | DCL p50/p90/max | Load p50/p90/max | Readiness p50/p90/max | LCP |
|---|---|---:|---:|---:|---:|---|---|---|---|---|
| E0 | cold / warm | 11 | 10 | 1 | 0.09090909090909091 | 1.800000011920929 / 5.600000023841858 / 6.699999988079071 | 831.2000000178814 / 1800.2000000178814 / 2748.0999999940395 | 837.2000000178814 / 1806.4000000059605 / 2753.0999999940395 | 1053.0999999940395 / 2107.300000011921 / 2964.199999988079 | not_available (all null) |
| L20 | cold / warm | 10 | 10 | 0 | 0.0 | 1.5999999940395355 / 2.5 / 2.600000023841858 | 714.8000000119209 / 865.7999999821186 / 1198.7000000178814 | 721.4000000059605 / 872.8999999761581 / 1203.2000000178814 | 941.6999999880791 / 1077.199999988079 / 1419.4000000059605 | not_available (all null) |
| D1 | cold / warm | 10 | 10 | 0 | 0.0 | 4.100000023841858 / 6.199999988079071 / 47.099999994039536 | 747.2999999821186 / 885.4000000059605 / 999.0 | 748.1999999880791 / 886.0999999940395 / 999.6999999880791 | 1339.0999999940395 / 1415.0 / 1581.300000011921 | not_available (all null) |
| M30 | cold / warm | 10 | 10 | 0 | 0.0 | 2.800000011920929 / 3.0999999940395355 / 5.299999982118607 | 864.7000000178814 / 1823.4000000059605 / 2104.2000000178814 | 871.5999999940395 / 1830.0 / 2110.7000000178814 | 15.099999994039536 / 24.399999976158142 / 36.400000005960464 | not_available (all null) |

## Key API timing source

Durations below come from the raw timing fields only. HTTP status is kept as a separate status overview and is never treated as a duration.

### E0

| Endpoint/path | Source | Count | p50 | p90 | Max |
|---|---|---:|---:|---:|---:|
| `/api/notes?status=published&page=1&size=20` | raw sample field required_api[].duration; status remains in the raw required_api[].status field and is not used as a duration | 10 | 91.80000001192093 | 122.0 | 129.40000000596046 |

### L20

| Endpoint/path | Source | Count | p50 | p90 | Max |
|---|---|---:|---:|---:|---:|
| `/api/notes?status=published&page=1&size=20` | raw sample field required_api[].duration; status remains in the raw required_api[].status field and is not used as a duration | 10 | 92.19999998807907 | 119.69999998807907 | 123.69999998807907 |

### D1

| Endpoint/path | Source | Count | p50 | p90 | Max |
|---|---|---:|---:|---:|---:|
| `/api/notes/pra04-d1` | raw sample field required_api[].duration; status remains in the raw required_api[].status field and is not used as a duration | 10 | 5.4000000059604645 | 9.0 | 10.599999994039536 |

### M30

| Endpoint/path | Source | Count | p50 | p90 | Max |
|---|---|---:|---:|---:|---:|
| `/api/admin/dashboard/summary` | raw sample field api_timings[].duration grouped by URL path; HTTP status is reported separately and never used as latency | 10 | 9.400000005960464 | 12.400000005960464 | 18.0 |
| `/api/ai/suggestions` | raw sample field api_timings[].duration grouped by URL path; HTTP status is reported separately and never used as latency | 10 | 7.700000017881393 | 11.400000005960464 | 18.900000005960464 |
| `/api/auth/login` | raw sample field api_timings[].duration grouped by URL path; HTTP status is reported separately and never used as latency | 10 | 175.30000001192093 | 180.69999998807907 | 199.19999998807907 |
| `/api/auth/me` | raw sample field api_timings[].duration grouped by URL path; HTTP status is reported separately and never used as latency | 20 | 1.5 | 2.199999988079071 | 8.0 |
| `/api/auth/passkey/status` | raw sample field api_timings[].duration grouped by URL path; HTTP status is reported separately and never used as latency | 10 | 2.5 | 3.300000011920929 | 3.5 |
| `/api/content/site-settings` | raw sample field api_timings[].duration grouped by URL path; HTTP status is reported separately and never used as latency | 10 | 2.5 | 3.5999999940395355 | 15.400000005960464 |
| `/api/folders` | raw sample field api_timings[].duration grouped by URL path; HTTP status is reported separately and never used as latency | 10 | 5.4000000059604645 | 9.800000011920929 | 14.400000005960464 |
| `/api/music/manage/daily-song/public` | raw sample field api_timings[].duration grouped by URL path; HTTP status is reported separately and never used as latency | 10 | 1.5999999940395355 | 1.800000011920929 | 11.200000017881393 |
| `/api/notes?page=1&size=30` | raw sample field api_timings[].duration grouped by URL path; HTTP status is reported separately and never used as latency | 10 | 8.099999994039536 | 12.599999994039536 | 15.300000011920929 |
| `/api/tags` | raw sample field api_timings[].duration grouped by URL path; HTTP status is reported separately and never used as latency | 10 | 5.5 | 9.899999976158142 | 14.199999988079071 |

Authentication/session status overview (not latency):

```json
{
  "login_response_status_counts": {
    "200": 10
  },
  "auth_me_status_counts": {
    "200": 20,
    "401": 10
  },
  "strict_management_status_counts": {
    "200": 10
  },
  "interpretation": "HTTP status counts are authorization/session evidence only; they are not latency values."
}
```

## Input and exclusion proof

The JSON artifact records every explicit input path and SHA-256. Smoke, health-check, server-cold, and M30 negative-boundary artifacts are listed under `separate_or_excluded_artifacts` and are not in the primary scenario counts.

## Remaining boundary

E0 retains one failed raw row; all four primary scenarios have at least 10 valid rows. No server-cold aggregate was produced. Observations and optimization candidates are unverified suggestions only. PRA-08 final cleanup and integrity review is PASS.
