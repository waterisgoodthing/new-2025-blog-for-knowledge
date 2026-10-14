"""PR-09 scratch evidence: constraint rejection + visibility='public' acceptance."""

import asyncio

from sqlalchemy import text

from app.utils.scratch_db_safety import require_scratch_database
from app.config import get_settings

require_scratch_database(get_settings().DATABASE_URL)

from app.database import async_session, engine


async def main() -> None:
    async with async_session() as s:
        sid = (await s.execute(text(
            "INSERT INTO subjects (name) VALUES ('pr09-ev1') RETURNING id"
        ))).scalar_one()
        mdi = (await s.execute(text(
            "INSERT INTO draft_items (id,draft_type,source_type,source_id,status,version,"
            "target_type,target_id,source_hash,approved_by,approved_at,conversion_sequence,"
            "target_mistake_id) VALUES (gen_random_uuid(),'mistake','question','q1',"
            "'converted',1,'mistake','t',repeat('a',64),gen_random_uuid(),now(),1,"
            "gen_random_uuid()) RETURNING id"
        ))).scalar_one()
        qid = (await s.execute(text(
            "INSERT INTO questions (id,subject_id,stem_md,question_text,question_type,"
            "options,answer_data,correct_answer,status,visibility,version) "
            "VALUES (gen_random_uuid(),:s,'','q','short_answer','[]','{}','a',"
            "'active','private',1) RETURNING id"
        ), {"s": sid})).scalar_one()
        mk = (await s.execute(text(
            "INSERT INTO mistakes (id,source_draft_item_id,question_id,subject_id,"
            "question_text,reason_category,status,visibility,version) "
            "VALUES (gen_random_uuid(),:d,:q,:s,'q','unknown','active','public',1) "
            "RETURNING id"
        ), {"d": mdi, "q": qid, "s": sid})).scalar_one()
        await s.commit()
        print(f"CREATED_MISTAKE_ID={mk}")

        try:
            await s.execute(
                text("UPDATE mistakes SET visibility='x' WHERE id=:id"), {"id": mk}
            )
            await s.commit()
            print("FAIL: visibility=x accepted")
        except Exception as exc:
            await s.rollback()
            print(f"PASS: visibility=x rejected ({type(exc).__name__})")

        vis = (await s.execute(
            text("SELECT visibility FROM mistakes WHERE id=:id"), {"id": mk}
        )).scalar_one()
        print(f"CURRENT_VISIBILITY={vis}")


asyncio.run(main())
