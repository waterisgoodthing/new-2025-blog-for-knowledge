"""Unit tests for the in-memory login throttle (PR-16 / W4-D04).

Pure unit tests: no database access. ``reset_state`` is called before every
case so module-global counters never leak between tests.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.config import parse_login_throttle_delays
from app.services import login_throttle as lt


def _settings(
    *,
    enabled: bool = True,
    delays: str = "2,5,15",
    threshold: int = 3,
    ip_ttl: int = 3600,
    max_failures: int = 10,
    max_accounts: int = 10_000,
) -> SimpleNamespace:
    return SimpleNamespace(
        LOGIN_THROTTLE_ENABLED=enabled,
        LOGIN_THROTTLE_WARN_THRESHOLD=threshold,
        LOGIN_THROTTLE_DELAYS=delays,
        LOGIN_THROTTLE_IP_TTL_SECONDS=ip_ttl,
        LOGIN_THROTTLE_ACCOUNT_MAX_FAILURES=max_failures,
        LOGIN_THROTTLE_MAX_ACCOUNTS=max_accounts,
    )


@pytest.fixture(autouse=True)
def _clean_state():
    lt.reset_state()
    yield
    lt.reset_state()


def test_parse_delays_returns_floats_in_order():
    assert parse_login_throttle_delays("2,5,15") == [2.0, 5.0, 15.0]


def test_parse_delays_ignores_blank_invalid_and_negative():
    assert parse_login_throttle_delays(" 1 , ,x, -3, 0.5 ") == [1.0, 0.5]
    assert parse_login_throttle_delays("") == []
    assert parse_login_throttle_delays(None) == []


def test_delay_schedule_graduated_and_capped():
    settings = _settings()
    sequence = []

    # Each iteration inspects the delay for the *next* attempt before recording
    # that attempt's failure.
    for _ in range(8):
        sequence.append(lt.get_required_delay("alice", "10.0.0.1", settings))
        lt.record_failure("alice", "10.0.0.1")

    assert sequence == [0.0, 0.0, 0.0, 2.0, 5.0, 15.0, 15.0, 15.0]


def test_no_failures_means_no_delay():
    assert lt.get_required_delay("nobody", "10.0.0.2", _settings()) == 0.0


def test_account_counter_resets_on_success():
    settings = _settings()
    for _ in range(3):
        lt.record_failure("bob", None)
    assert lt.get_required_delay("bob", "fresh-ip", settings) == 2.0

    lt.record_success("bob")
    assert lt.get_required_delay("bob", "fresh-ip", settings) == 0.0


def _freeze_clock(monkeypatch, start: float = 1000.0, ip_ttl: int = 3600):
    clock = {"t": start}
    monkeypatch.setattr(lt, "_now", lambda: clock["t"])
    monkeypatch.setattr(lt, "_ip_ttl_seconds", lambda: ip_ttl)
    return clock


def test_ip_counter_decays_after_ttl(monkeypatch):
    settings = _settings(ip_ttl=3600)
    clock = _freeze_clock(monkeypatch)

    for _ in range(3):
        lt.record_failure(None, "203.0.113.7")
    assert lt.get_required_delay(None, "203.0.113.7", settings) == 2.0

    clock["t"] += settings.LOGIN_THROTTLE_IP_TTL_SECONDS - 1
    assert lt.get_required_delay(None, "203.0.113.7", settings) == 2.0

    clock["t"] += 2
    assert lt.get_required_delay(None, "203.0.113.7", settings) == 0.0
    # The read path evicts the expired entry instead of leaving it to revive.
    assert "203.0.113.7" not in lt._ips


def test_failure_after_ttl_restarts_ip_count(monkeypatch):
    settings = _settings(ip_ttl=3600)
    clock = _freeze_clock(monkeypatch)

    for _ in range(3):
        lt.record_failure(None, "203.0.113.8")
    assert lt.get_required_delay(None, "203.0.113.8", settings) == 2.0

    clock["t"] += 3601
    # Previously this revived 3 -> 4 and returned 5s. It must restart at 1 -> 0s.
    lt.record_failure(None, "203.0.113.8")
    assert lt.get_failure_count(None, "203.0.113.8", settings) == 1
    assert lt.get_required_delay(None, "203.0.113.8", settings) == 0.0


def test_expired_ip_entries_are_evicted(monkeypatch):
    settings = _settings(ip_ttl=3600)
    clock = _freeze_clock(monkeypatch)

    for index in range(50):
        lt.record_failure(None, f"203.0.{index // 256}.{index % 256}")
    assert len(lt._ips) == 50

    clock["t"] += 3601
    lt.record_failure(None, "198.51.100.200")
    # The write-path sweep drops every stale IP; only the fresh one remains.
    assert len(lt._ips) == 1
    assert "198.51.100.200" in lt._ips


def _bounded_settings(monkeypatch, max_accounts: int):
    """Lower the process-wide account capacity for a test.

    ``_max_accounts`` reads the cached settings singleton, so patch the service
    helper directly rather than the settings object.
    """
    monkeypatch.setattr(lt, "_max_accounts", lambda: max_accounts)


def test_overlong_username_key_is_bounded(monkeypatch):
    _bounded_settings(monkeypatch, 10_000)
    huge = "x" * 100_000

    lt.record_failure(huge, None)

    assert len(lt._accounts) == 1
    (key,) = lt._accounts.keys()
    assert len(key) <= lt._MAX_ACCOUNT_KEY_LENGTH + len("sha256:")
    assert key.startswith("sha256:")
    # The retained key is a fixed-size digest, not the 100,000-char input.
    assert key != huge
    assert len(huge) > len(key)


def test_overlong_username_still_accumulates_on_one_entry(monkeypatch):
    _bounded_settings(monkeypatch, 10_000)
    huge = "y" * 5_000
    settings = _settings()

    for _ in range(3):
        lt.record_failure(huge, None)

    # Same over-long username hashes to the same key, so the protection holds.
    assert len(lt._accounts) == 1
    assert lt.get_failure_count(huge, None, settings) == 3
    assert lt.get_required_delay(huge, "fresh-ip", settings) == 2.0


def test_distinct_overlong_usernames_do_not_collide(monkeypatch):
    _bounded_settings(monkeypatch, 10_000)
    shared_prefix = "z" * 10_000

    lt.record_failure(shared_prefix + "a", None)
    lt.record_failure(shared_prefix + "b", None)

    # Distinct usernames get distinct bounded keys (no shared-prefix collision).
    assert len(lt._accounts) == 2


def test_short_username_keys_are_stored_verbatim(monkeypatch):
    _bounded_settings(monkeypatch, 10_000)
    lt.record_failure("alice", None)
    assert "alice" in lt._accounts


def test_capacity_evicts_least_recently_updated(monkeypatch):
    _bounded_settings(monkeypatch, 5)
    settings = _settings()

    for index in range(5):
        lt.record_failure(f"user-{index}", None)
    assert len(lt._accounts) == 5

    # Touch user-0 so it is now the most recently updated, then overflow.
    lt.record_failure("user-0", None)
    lt.record_failure("user-5", None)

    assert len(lt._accounts) == 5
    # user-1 was the least recently updated and is evicted; user-0 survives.
    assert "user-0" in lt._accounts
    assert "user-5" in lt._accounts
    assert "user-1" not in lt._accounts
    # Evicted account loses its counter; surviving account keeps its count.
    assert lt.get_failure_count("user-0", None, settings) == 2
    assert lt.get_failure_count("user-1", None, settings) == 0


def test_account_map_stays_bounded_under_flood(monkeypatch):
    _bounded_settings(monkeypatch, 50)
    for index in range(500):
        lt.record_failure(f"random-{index}", None)

    assert len(lt._accounts) == 50
    # Only the 50 most recent survive; the oldest 450 are gone.
    assert "random-499" in lt._accounts
    assert "random-0" not in lt._accounts


def test_capacity_eviction_preserves_cross_ip_protection(monkeypatch):
    _bounded_settings(monkeypatch, 1000)
    settings = _settings()

    for _ in range(3):
        lt.record_failure("legitimate", None)
    # Fill the map without evicting "legitimate" (1000 capacity, <1000 others).
    for index in range(100):
        lt.record_failure(f"noise-{index}", None)

    # The legitimate account still throttles a brand-new IP.
    assert lt.get_required_delay("legitimate", "198.51.100.77", settings) == 2.0


def test_account_counters_do_not_decay_with_ip_ttl(monkeypatch):
    settings = _settings(ip_ttl=3600)
    clock = _freeze_clock(monkeypatch)

    for _ in range(3):
        lt.record_failure("heidi", None)
    assert lt.get_required_delay("heidi", "fresh-ip", settings) == 2.0

    clock["t"] += 10_000_000
    # Account TTL is intentionally not applied: the account dimension must
    # survive across IP changes.
    assert lt.get_required_delay("heidi", "fresh-ip", settings) == 2.0


def test_disabled_throttle_never_delays():
    settings = _settings(enabled=False)
    for _ in range(10):
        lt.record_failure("carol", "10.0.0.9")
    assert lt.get_required_delay("carol", "10.0.0.9", settings) == 0.0


def test_account_dimension_persists_across_ips():
    settings = _settings()
    for _ in range(3):
        lt.record_failure("dave", None)
    # A brand-new IP has no failures, but the account counter still forces 2s.
    assert lt.get_required_delay("dave", "198.51.100.55", settings) == 2.0


def test_ip_dimension_triggers_for_a_different_account():
    settings = _settings()
    for _ in range(3):
        lt.record_failure(None, "198.51.100.66")
    # Fresh account, but the shared IP has hit the threshold.
    assert lt.get_required_delay("brand-new-account", "198.51.100.66", settings) == 2.0


def test_failure_count_reports_stricter_dimension():
    settings = _settings()
    for _ in range(4):
        lt.record_failure("erin", "192.0.2.10")
    assert lt.get_failure_count("erin", "192.0.2.10", settings) == 4
    assert lt.get_failure_count("erin", "unseen-ip", settings) == 4
    assert lt.get_failure_count("unseen-account", "192.0.2.10", settings) == 4


def test_failure_count_grows_past_alert_threshold():
    # The account counter is not capped; LOGIN_THROTTLE_ACCOUNT_MAX_FAILURES is
    # an alerting threshold used by the router, not a lockout.
    settings = _settings(delays="1,2,3", max_failures=5)
    for _ in range(12):
        lt.record_failure("frank", None)
    assert lt.get_failure_count("frank", None, settings) == 12
    assert lt.get_required_delay("frank", None, settings) == 3.0
