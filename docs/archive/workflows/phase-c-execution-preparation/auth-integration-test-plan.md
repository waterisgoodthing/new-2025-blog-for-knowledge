# Permission Integration Test Plan

日期：2026-07-13  
状态：设计完成；未修改权限代码、认证配置或数据。

## Scope and Identity Model

身份：`public`、`authenticated user`、`admin`、`worker`。对象：`notes`、`questions`、`mistakes`、`review_items`、`attachments`、`ai_runs`。当前证据确认已有部分 admin/anonymous coverage，但 authenticated-user owner isolation、worker boundary、cross-owner integration evidence 缺失。

目标态的 allow/deny 如下；不是当前实现已完成的声明。

| Object | Allow cases | Deny cases | Expected status | Security risk |
|---|---|---|---|---|
| notes | public read published+not hidden；user own；admin authorized | public write/management；user other owner；worker browser direct | public read 200；unauthorized 401/403；hidden/private not found or 403 per contract | public leakage、cross-owner read/write |
| questions | user own；admin authorized；worker trusted task | public private/read-write；user other owner；worker missing/invalid owner | 200/201 for allow；401/403 for deny | subject mistaken for owner、worker spoofing |
| mistakes | public legacy Note only when published+not hidden；user own private; admin authorized | independent private mistake public；user other owner；target mismatch | 200 allow；401/403 or non-disclosure deny | legacy/independent dual-source leakage |
| review_items | user own queue/submit；admin authorized; trusted worker for verified owner | public; user other target; worker replay/mismatch | 200/204 allow；401/403 deny | polymorphic target cross-owner, review history tampering |
| attachments | user own metadata/content; admin governance; worker trusted owner-scoped operation | public; other owner; link target mismatch; browser worker spoof | 200 allow；401/403/404 deny per non-disclosure policy | blob leakage, storage-key disclosure |
| ai_runs | user own safe detail; admin authorized query/decision/retry; worker original-owner task | public; other owner; unauthorized replay/decision; target mismatch | 200 allow；401/403 deny | sensitive input/output and replay authorization |

## Required Integration Cases

For every object above, create fixtures for owner A, owner B, admin, public/no token, and a trusted worker task. Run:

1. own-object read/write/action: expected allow where contract permits;
2. other-owner object read/write/action: expected deny and no sensitive payload;
3. anonymous/public filtering: published public content only; private/hidden/unpublished and admin errors do not leak;
4. polymorphic target mismatch: wrong `target_type`, nonexistent `target_id`, object belonging to another owner; expected deny;
5. worker boundary: browser token/header cannot impersonate worker; worker requires trusted task identity, owner ID, object ID, schema version and idempotency key;
6. AI replay authorization: replay/retry/decision must validate original target owner and action scope; repeated idempotency key must not create unauthorized duplicate action;
7. sensitive-field leakage: assert response/log does not expose `replay_input`, raw output, `input_summary`, authorization/cookie/token fields, or storage internals beyond approved contract;
8. admin scope: admin route works only with `get_current_admin` and does not convert admin identity into business owner.

## AUTH_BYPASS Three-State Matrix

| `AUTH_BYPASS` | `AUTH_BYPASS_ALLOW` | Expected | Test purpose |
|---|---|---|---|
| false | false | normal auth enforced | baseline |
| true | false | normal auth enforced | single flag cannot bypass |
| false | true | normal auth enforced | allow flag alone cannot bypass |
| true | true | local-only bypass behavior may occur; production must reject startup | verify explicit development boundary; never use as normal permission proof |

The current evidence says bypass semantics are `return bypass and allow`; production startup rejection for the double-true combination is a later P2 hardening item and is not implemented by this plan.

## Pass Criteria

- all allow cases return only owner-scoped and contract-approved fields;
- all deny cases return expected 401/403/non-disclosure behavior;
- no cross-owner object, link, target, blob or AI payload is observable;
- worker cannot be invoked as a browser identity and rejects mismatched owner/target;
- all four AUTH_BYPASS combinations are recorded, with double-true never accepted as production readiness;
- tests run against isolated fixtures and do not rely on bypass to prove authorization.

Until this evidence exists, `AUTH_READY` remains BLOCKED.

