# Design

## 1. Evidence Gap

The completed probe established measurement feasibility but used an empty isolated database and a development server. API `responseEnd` was a proxy because the application exposes no stable content-ready mark. The follow-up must close both gaps before setting a release budget.

## 2. Readiness Contract

Target pages expose stable states on their main content region:

```html
<main data-render-state="loading|ready|empty|error"></main>
```

When a successful ready or empty state commits, the page records one route-specific Performance Mark, for example:

- `notes:list-ready`;
- `notes:detail-ready`;
- `manage:auth-submit`;
- `manage:content-ready`.

Marks must contain no slug, username, content, token or other personal data. The smallest existing component should own the mark; do not introduce a broad performance framework for three consumers.

## 3. Dataset Profiles

| Profile | Purpose                | Synthetic content                                                                             |
| ------- | ---------------------- | --------------------------------------------------------------------------------------------- |
| E0      | Empty-state regression | no published notes                                                                            |
| L20     | Full first list page   | 20 published notes with deterministic titles/tags                                             |
| D1      | Detail rendering       | one published Markdown-heavy note with headings, code, table, links and safe media references |
| M30     | Management list        | 30 mixed note/blog/mistake records, including drafts hidden from anonymous users              |

The dataset is created only in the isolated database. Public visibility assertions must confirm draft/hidden records do not leak.

## 4. Scenario Matrix

| Scenario            | Start             | Ready condition                                    |
| ------------------- | ----------------- | -------------------------------------------------- |
| Anonymous notes E0  | navigation start  | `data-render-state=empty` and `notes:list-ready`   |
| Anonymous notes L20 | navigation start  | 20 visible records and `notes:list-ready`          |
| Anonymous detail D1 | navigation start  | rendered article and `notes:detail-ready`          |
| Admin login M30     | login submit mark | management list settled and `manage:content-ready` |

Each server-warm scenario uses at least 10 new browser contexts. Server-cold samples are stored separately and never merged with browser-cold/server-warm samples.

## 5. Metrics

- Navigation: TTFB, DOMContentLoaded, load;
- Web rendering: LCP when available, route readiness mark;
- API: start, responseEnd, duration, status and slowest required request;
- business readiness: login-submit-to-manage-ready;
- quality: console errors, failed requests, duplicate requests and incorrect protected/public calls.

Report p50, p90, maximum and failure count. Raw samples must remain in `assets/` as machine-readable data where practical.

## 6. Environment

```text
fresh browser contexts
      -> isolated production frontend build
      -> isolated FastAPI
      -> isolated PostgreSQL at current migration
      -> deterministic synthetic seed
```

The production frontend must point only to the isolated backend through an explicitly verified hostname. If current production guards make this impossible without modifying machine-wide DNS or using the real API, execution stops for an environment decision.

## 7. Decision Rule

This task produces an evidence-backed budget proposal. It does not silently turn the broad plan's historical “LCP < 2.5s” or “route < 100ms” statements into achieved requirements. Any optimization work discovered is routed to a new approved task.
