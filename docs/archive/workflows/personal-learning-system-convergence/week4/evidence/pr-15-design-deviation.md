# PR-15 design deviation — W4-E08: raw WebAuthn challenge retained

Status: APPROVED deviation from the PR-15 task text (`tasks/pr-15.md` schema sketch).
Recorded by: main agent in `evidence/w4-00-decisions.md`.
Implemented by: PR-15 rework.

## Planned schema (task text)

`tasks/pr-15.md` §"Schema Design (W4-D03)" specified `webauthn_challenges` with
`challenge_hash VARCHAR(64) NOT NULL` and rationalised "`challenge_hash` instead of
raw challenge: challenges are random bytes, hash prevents size/encoding issues".

## Shipped schema

`033_webauthn_challenges.py` / `app/models/webauthn_challenge.py` ship **both**:

| Column | Type | Purpose |
|---|---|---|
| `challenge` | `VARCHAR(128) NOT NULL` | b64url-encoded raw challenge bytes |
| `challenge_hash` | `VARCHAR(64) NOT NULL` | sha256 hex of the raw bytes |

## Rationale (why the hash-only schema is not viable)

The shipped flow verifies the ceremony server-side with the `webauthn` library, calling
`verify_registration_response(expected_challenge=...)` /
`verify_authentication_response(expected_challenge=...)`. The library requires the
**exact raw challenge bytes** generated at option-creation time; a one-way sha256 hash
cannot be fed back into that comparison. Dropping the raw column would break all three
ceremonies (there is no other server-side copy — PR-15 explicitly replaces the in-memory
dicts that previously held the raw bytes).

`challenge_hash` is retained alongside as the sha256 lookup/integrity form (PR-15
review checklist: "Hash function is SHA-256"). It is the only digest-shaped field;
the raw value is a bounded 32-byte secret.

## Security treatment of the raw column

- The raw challenge is stored only as b64url in `webauthn_challenges.challenge`.
- No log statement interpolates the raw challenge, `challenge_hash`, or
  `expected_challenge` (verified by grep over `passkey_service.py` and
  `webauthn_challenge_service.py`; the only "challenge" log lines are static
  "no challenge stored" messages and the cleanup-failure warning).
- Raw challenges are not exposed by any public route or response body beyond the
  ceremony options already returned to the caller's own browser.

## Consequence for reviewers

Treat this as an intentional, minimal superset of the planned schema, not an
unreviewed omission. The PR-15 doc's "No challenge plaintext in logs or database"
checklist item is scoped to **logs**; the DB necessarily holds the raw value for
verification. See W4-E08.
