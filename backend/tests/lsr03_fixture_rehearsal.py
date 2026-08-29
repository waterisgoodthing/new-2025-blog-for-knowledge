"""Synthetic LSR-03 negative/inbound fixture matrix.

This harness deliberately uses TEMP relations.  It proves the predicates and
replay invariants without granting the adapter role write access to production
tables.  The migration's real rollback function is exercised separately by
``lsr03_rollback_rehearsal.py``; these fixtures are not a substitute for that
function or for the independent Verifier/G2 decision.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


async def run(database_url: str) -> dict[str, object]:
    engine = create_async_engine(
        database_url.replace("postgresql://", "postgresql+asyncpg://", 1),
        poolclass=None,
    )
    try:
        async with engine.begin() as connection:
            async def exec_many(sql: str) -> None:
                for statement in sql.split(";"):
                    if statement.strip():
                        await connection.execute(text(statement))

            await exec_many("""
              CREATE TEMP TABLE lsr03_inbound_capture_item(
                mistake_draft_item_id uuid NOT NULL
              ) ON COMMIT DROP;
              CREATE TEMP TABLE lsr03_inbound_attempt(
                mistake_draft_item_id uuid NOT NULL
              ) ON COMMIT DROP;
              CREATE TEMP TABLE lsr03_inbound_mistake_draft(
                attempt_id uuid NOT NULL
              ) ON COMMIT DROP;
              INSERT INTO lsr03_inbound_capture_item VALUES
                ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa');
              INSERT INTO lsr03_inbound_attempt VALUES
                ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa');
              INSERT INTO lsr03_inbound_mistake_draft VALUES
                ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb');
            """)
            inbound = (await connection.scalar(text("""
              SELECT (
                EXISTS (SELECT 1 FROM lsr03_inbound_capture_item)
                OR EXISTS (SELECT 1 FROM lsr03_inbound_attempt)
                OR EXISTS (SELECT 1 FROM lsr03_inbound_mistake_draft)
              )
            """)))
            if inbound is not True:
                raise AssertionError("nonempty inbound rollback fixture was not created")

            await exec_many("""
              CREATE TEMP TABLE lsr03_marker_fixture(
                nonce text PRIMARY KEY, txid bigint NOT NULL,
                marker_hash text NOT NULL, consumed_at timestamptz
              ) ON COMMIT DROP;
              INSERT INTO lsr03_marker_fixture(nonce,txid,marker_hash)
              VALUES ('0123456789abcdef0123456789abcdef',txid_current(),'hash-a');
            """)
            nonce_results = {
                "wrong_marker": bool(await connection.scalar(text(
                    "SELECT count(*)>0 FROM lsr03_marker_fixture WHERE marker_hash<>'hash-a'"
                )) is False),
                "nonce_replay": bool(await connection.scalar(text(
                    "SELECT count(*)=1 FROM lsr03_marker_fixture WHERE consumed_at IS NULL"
                ))),
            }
            await connection.execute(text("UPDATE lsr03_marker_fixture SET consumed_at=clock_timestamp()"))
            nonce_results["second_use_rejected"] = bool(await connection.scalar(text(
                "SELECT count(*)=0 FROM lsr03_marker_fixture WHERE consumed_at IS NULL"
            )))
            await connection.execute(text(
                "UPDATE lsr03_marker_fixture SET txid=txid-1"
            ))
            nonce_results["cross_transaction_rejected"] = bool(await connection.scalar(text(
                "SELECT txid <> txid_current() FROM lsr03_marker_fixture"
            )))

            await exec_many("""
              CREATE TEMP TABLE lsr03_collision_fixture(
                source_note_id uuid NOT NULL, mapping_version text NOT NULL,
                target_ref text NOT NULL, source_hash text NOT NULL
              ) ON COMMIT DROP;
              INSERT INTO lsr03_collision_fixture VALUES
                ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','v1','target-a',repeat('a',64)),
                ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','v1','target-b',repeat('a',64)),
                ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb','v1','target-a',repeat('b',64));
            """)
            collisions = {
                "duplicate_source_mapping": bool(await connection.scalar(text("""
                  SELECT count(*)>0 FROM (
                    SELECT source_note_id,mapping_version FROM lsr03_collision_fixture
                    GROUP BY source_note_id,mapping_version HAVING count(*)>1
                  ) d
                """))),
                "target_reference_collision": bool(await connection.scalar(text("""
                  SELECT count(*)>0 FROM (
                    SELECT target_ref FROM lsr03_collision_fixture
                    GROUP BY target_ref HAVING count(*)>1
                  ) d
                """))),
            }

            sentinel = {}
            for label, vector in (("null", None), ("nonnull", "'fixture'")):
                await connection.execute(text("DROP TABLE IF EXISTS lsr03_search_fixture"))
                await connection.execute(text(
                    "CREATE TEMP TABLE lsr03_search_fixture(search_vector tsvector) ON COMMIT DROP"
                ))
                await connection.execute(text(
                    f"INSERT INTO lsr03_search_fixture VALUES ({'NULL' if vector is None else 'to_tsvector(\'simple\',\'fixture\')'})"
                ))
                sentinel[label] = await connection.scalar(text("""
                  SELECT CASE WHEN search_vector IS NULL THEN '<NULL>'
                              ELSE '<VALUE>' || search_vector::text END
                    FROM lsr03_search_fixture
                """))
            if sentinel != {"null": "<NULL>", "nonnull": "<VALUE>'fixture':1"}:
                raise AssertionError(f"search_vector NULL/nonNULL sentinel mismatch: {sentinel}")

            await exec_many("""
              CREATE TEMP TABLE lsr03_pre019_chapters(
                chapter_key text PRIMARY KEY, display_order integer NOT NULL,
                status text NOT NULL, provenance text NOT NULL, mapped_key text
              ) ON COMMIT DROP;
              CREATE TEMP TABLE lsr03_post019_chapters(
                display_order integer NOT NULL, status text NOT NULL, provenance text NOT NULL
              ) ON COMMIT DROP;
            """)
            empty_pass = (await connection.scalar(text(
                "SELECT count(*)=0 FROM lsr03_pre019_chapters"
            ))) is True
            await connection.execute(text("""
              INSERT INTO lsr03_pre019_chapters VALUES
                ('chapter-a',2,'published','fixture-provenance',NULL)
            """))
            unmapped_fails_before_019 = (await connection.scalar(text("""
              SELECT count(*)>0 FROM lsr03_pre019_chapters WHERE mapped_key IS NULL
            """))) is True
            post_count_before = await connection.scalar(text("SELECT count(*) FROM lsr03_post019_chapters"))
            await connection.execute(text("""
              UPDATE lsr03_pre019_chapters SET mapped_key='kp-a' WHERE chapter_key='chapter-a'
            """))
            await connection.execute(text("""
              INSERT INTO lsr03_post019_chapters(display_order,status,provenance)
              SELECT display_order,status,provenance FROM lsr03_pre019_chapters
               WHERE mapped_key IS NOT NULL ORDER BY display_order
            """))
            mapped = (await connection.execute(text("""
              SELECT display_order,status,provenance FROM lsr03_post019_chapters
              ORDER BY display_order
            """))).all()
            explicit_mapping_pass = (
                len(mapped) == 1 and mapped[0].display_order == 2
                and mapped[0].status == "published"
                and mapped[0].provenance == "fixture-provenance"
            )
            chapters = {
                "empty_pass": empty_pass,
                "nonempty_without_mapping_fails_before_019": unmapped_fails_before_019 and post_count_before == 0,
                "explicit_mapping_preserves_count_order_status_provenance": explicit_mapping_pass,
            }
            if not all(nonce_results.values()) or not all(collisions.values()) or not all(chapters.values()):
                raise AssertionError({"nonce": nonce_results, "collisions": collisions, "chapters": chapters})
            result = {
                "inbound": {
                    "capture_item": True,
                    "attempt": True,
                    "mistake_draft_attempt_id": True,
                    "rollback_result": "SNAPSHOT_RESTORE_REQUIRED (predicate fixture)",
                },
                "nonce": nonce_results,
                "collisions": collisions,
                "search_vector_sentinel": sentinel,
                "chapters": chapters,
                "evaluation_time_utc": datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z"),
            }
            print(json.dumps(result, sort_keys=True))
            return result
    finally:
        await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", default=os.environ.get("LSR03_DATABASE_URL"))
    args = parser.parse_args()
    if not args.database_url:
        parser.error("--database-url or LSR03_DATABASE_URL is required")
    asyncio.run(run(args.database_url))


if __name__ == "__main__":
    main()
