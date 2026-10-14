"""W3-D09 legacy mistake write-freeze guard (PR-09).

Single fail-closed predicate invoked at every legacy Note write-router entry
that could create, mutate or delete a ``Note(type='mistake')`` row. Compat
reads (K-1..K-12) are deliberately untouched.
"""

from __future__ import annotations

LEGACY_MISTAKE_TYPE = "mistake"
LEGACY_MISTAKE_WRITE_FROZEN_CODE = "legacy_mistake_write_frozen"
LEGACY_MISTAKE_WRITE_STATUS = 410

_MESSAGE = (
    "Legacy mistake note writes are frozen (W3-D09). "
    "Use the canonical mistake APIs instead."
)


class LegacyMistakeWriteFrozen(Exception):
    """Raised when a write path touches a legacy ``Note(type='mistake')``."""

    def __init__(self, operation: str) -> None:
        self.operation = operation
        self.code = LEGACY_MISTAKE_WRITE_FROZEN_CODE
        super().__init__(_MESSAGE)


def assert_not_legacy_mistake_write(*note_types: str | None, operation: str) -> None:
    """Fail closed when any supplied note type is the legacy mistake type.

    ``note_types`` accepts every type involved in the operation: the existing
    row's type and any target/request type. A single ``'mistake'`` anywhere in
    the set freezes the write (W3-D09 F-1..F-9).
    """
    for note_type in note_types:
        if note_type == LEGACY_MISTAKE_TYPE:
            raise LegacyMistakeWriteFrozen(operation)


def freeze_error_detail(operation: str) -> dict[str, str]:
    return {"code": LEGACY_MISTAKE_WRITE_FROZEN_CODE, "operation": operation, "message": _MESSAGE}
