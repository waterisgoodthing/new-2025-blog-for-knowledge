"""In-memory dual-dimension login throttling (W4-D04 / W4-E04).

Tracks failed password-login attempts per account (``username``) and per client
IP, and reports the graduated delay a caller must wait *before* attempting
authentication. Account and IP counters are combined with ``max`` so the
stricter dimension wins.

Limitations (documented by design, not defects):

* State lives in this process's memory only. Restarting the process -- or
  scaling to multiple workers/instances -- resets every counter and each
  instance keeps its own view. Throttling therefore raises the cost of
  brute-force attempts against one process; it is neither durable nor
  cluster-coherent. A shared store (e.g. Redis) would be required for that.
* IP counters decay by TTL. An entry whose age exceeds
  ``LOGIN_THROTTLE_IP_TTL_SECONDS`` is *expired*: reads evict the accessed
  entry and report it as absent, and the write path replaces an expired entry
  with a fresh counter (its count restarts at 1). Every write also sweeps all
  other expired IP entries, so ``_ips`` cannot grow without bound.
* Account counters do **not** decay with time. They persist until a successful
  login (``record_success``), capacity eviction, or a process restart. This is
  deliberate: the account dimension is the IP-spoofing mitigation and must
  survive across address changes, so applying the IP TTL to accounts would
  weaken it. ``LOGIN_THROTTLE_ACCOUNT_MAX_FAILURES`` is an alerting threshold
  (see ``get_failure_count``), not a lockout.
* Account state is bounded on two axes so attacker-controlled usernames cannot
  grow it without limit:
  * **Key length** -- an account key longer than ``_MAX_ACCOUNT_KEY_LENGTH``
    (256) characters is replaced by ``"sha256:" + sha256(key).hexdigest()``
    (71 chars). Normal usernames are stored verbatim, so existing behavior is
    unchanged; only over-long input is hashed, which also avoids a
    shared-prefix collision between two distinct long usernames.
  * **Capacity** -- ``LOGIN_THROTTLE_MAX_ACCOUNTS`` (default 10000) caps the
    number of account entries. On overflow the least-recently-updated entries
    are evicted (``_accounts`` is an ``OrderedDict`` and every write moves the
    touched key to the end). Because the IP dimension is independently
    TTL-evicted, a flood of distinct nonexistent usernames is bounded even
    though account counters do not decay.
  Eviction is the deliberate trade-off: an attacker who can fill the account
  table can evict a legitimate account's counter, but cannot make memory grow
  without bound, and the IP dimension still applies.

Delays are computed from the failure count already recorded, so the first
``LOGIN_THROTTLE_WARN_THRESHOLD`` attempts are unthrottled and the next attempt
uses ``delays[0]``, then ``delays[1]``, and so on, saturating at the last value.
"""

from __future__ import annotations

import hashlib
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field

from app.config import parse_login_throttle_delays

_DEFAULT_IP_TTL_SECONDS = 3600
_DEFAULT_MAX_ACCOUNTS = 10_000

#: Account keys longer than this are hashed (see module docstring).
_MAX_ACCOUNT_KEY_LENGTH = 256


def _now() -> float:
    """Monotonic clock indirection so tests can control the TTL timeline."""
    return time.monotonic()


def _ip_ttl_seconds() -> int:
    """Configured IP-entry TTL in seconds, with a safe default on config error."""
    from app.config import get_settings

    try:
        value = int(get_settings().LOGIN_THROTTLE_IP_TTL_SECONDS)
    except Exception:
        return _DEFAULT_IP_TTL_SECONDS
    return value if value > 0 else _DEFAULT_IP_TTL_SECONDS


def _is_expired(counter: "_Counter", ttl_seconds: int, now: float) -> bool:
    return ttl_seconds > 0 and (now - counter.updated_at) > ttl_seconds


@dataclass
class _Counter:
    failures: int = 0
    updated_at: float = field(default_factory=lambda: _now())


_accounts: "OrderedDict[str, _Counter]" = OrderedDict()
_ips: dict[str, _Counter] = {}
_lock = threading.Lock()


def _max_accounts() -> int:
    """Configured account-entry capacity, with a safe default on config error."""
    from app.config import get_settings

    try:
        value = int(get_settings().LOGIN_THROTTLE_MAX_ACCOUNTS)
    except Exception:
        return _DEFAULT_MAX_ACCOUNTS
    return value if value > 0 else _DEFAULT_MAX_ACCOUNTS


def _account_key(account: str) -> str:
    """Bound the per-entry key length for attacker-controlled account names.

    Names within ``_MAX_ACCOUNT_KEY_LENGTH`` are kept verbatim (existing
    behavior). Longer names collapse to a fixed-size SHA-256 digest; the hash
    is stable, so repeated failures for the same long username still accumulate
    on one entry, while two distinct long usernames cannot collide via a
    shared prefix.
    """
    if len(account) <= _MAX_ACCOUNT_KEY_LENGTH:
        return account
    digest = hashlib.sha256(account.encode("utf-8", "surrogatepass")).hexdigest()
    return f"sha256:{digest}"


def reset_state() -> None:
    """Clear all counters. Intended for tests and process-level resets."""
    with _lock:
        _accounts.clear()
        _ips.clear()


def _evict_expired(store: dict[str, _Counter], ttl_seconds: int, now: float) -> None:
    """Drop every expired entry from ``store`` (must be called under ``_lock``)."""
    if ttl_seconds <= 0:
        return
    stale = [key for key, counter in store.items() if _is_expired(counter, ttl_seconds, now)]
    for key in stale:
        del store[key]


def _evict_overflow_accounts(store: "OrderedDict[str, _Counter]", max_entries: int) -> None:
    """Keep at most ``max_entries`` account counters (must hold ``_lock``).

    Evicts the least-recently-updated entries first, i.e. from the front of the
    ``OrderedDict``; every write moves its key to the end, so the tail is the
    most recently updated. This bounds ``_accounts`` as a whole rather than the
    key length only, so an attacker sending distinct random usernames cannot
    grow it without limit.
    """
    while len(store) > max_entries:
        store.popitem(last=False)


def _live_count(
    store: dict[str, _Counter], key: str | None, ttl_seconds: int, now: float
) -> int:
    """Return the live count for ``key``, evicting it first if expired.

    Must be called under ``_lock``. An expired entry is removed and reported as
    absent rather than merely returning 0, so it cannot be revived later.
    """
    if not key:
        return 0
    counter = store.get(key)
    if counter is None:
        return 0
    if _is_expired(counter, ttl_seconds, now):
        del store[key]
        return 0
    return counter.failures


def record_failure(account: str | None, ip: str | None) -> None:
    """Increment the account and/or IP failure counters for a failed attempt.

    An expired IP entry is replaced with a fresh counter instead of being
    incremented, and other expired IP entries are swept, so TTL expiry genuinely
    restarts the count and the IP map stays bounded.
    """
    now = _now()
    ip_ttl = _ip_ttl_seconds()
    max_accounts = _max_accounts()
    with _lock:
        if account:
            key = _account_key(account)
            counter = _accounts.get(key)
            if counter is None:
                counter = _Counter()
            counter.failures += 1
            counter.updated_at = now
            _accounts[key] = counter
            _accounts.move_to_end(key)
            _evict_overflow_accounts(_accounts, max_accounts)
        if ip:
            _evict_expired(_ips, ip_ttl, now)
            counter = _ips.get(ip)
            if counter is None:
                counter = _Counter()
                _ips[ip] = counter
            counter.failures += 1
            counter.updated_at = now


def record_success(account: str | None) -> None:
    """Reset the account counter after a successful login."""
    if not account:
        return
    with _lock:
        _accounts.pop(_account_key(account), None)


def _delay_for(failures: int, threshold: int, delays: list[float]) -> float:
    # The first ``threshold`` attempts are free; the next attempt (with
    # ``failures == threshold`` recorded) waits ``delays[0]``, then ``delays[1]``
    # and so on, saturating at the final entry.
    if failures < threshold or not delays:
        return 0.0
    index = failures - threshold
    if index >= len(delays):
        index = len(delays) - 1
    return delays[index]


def get_required_delay(account: str | None, ip: str | None, settings) -> float:
    """Seconds to wait before attempting login (``max(account, ip)``)."""
    if not getattr(settings, "LOGIN_THROTTLE_ENABLED", True):
        return 0.0

    delays = parse_login_throttle_delays(getattr(settings, "LOGIN_THROTTLE_DELAYS", ""))
    if not delays:
        return 0.0
    threshold = int(getattr(settings, "LOGIN_THROTTLE_WARN_THRESHOLD", 3))
    ip_ttl = int(getattr(settings, "LOGIN_THROTTLE_IP_TTL_SECONDS", 3600))
    now = _now()

    with _lock:
        account_failures = _live_count(
            _accounts, _account_key(account) if account else None, 0, now
        )
        ip_failures = _live_count(_ips, ip, ip_ttl, now)

    return max(
        _delay_for(account_failures, threshold, delays),
        _delay_for(ip_failures, threshold, delays),
    )


def get_failure_count(account: str | None, ip: str | None, settings) -> int:
    """Live failure count across both dimensions (used for WARN logging)."""
    ip_ttl = int(getattr(settings, "LOGIN_THROTTLE_IP_TTL_SECONDS", 3600))
    now = _now()
    with _lock:
        account_failures = _live_count(
            _accounts, _account_key(account) if account else None, 0, now
        )
        ip_failures = _live_count(_ips, ip, ip_ttl, now)
    return max(account_failures, ip_failures)
