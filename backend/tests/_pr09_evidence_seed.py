"""PR-09 scratch evidence: seed legacy mistake notes for wk3 runner matrix."""

import asyncio

from sqlalchemy import text

from app.utils.scratch_db_safety import require_scratch_database
from app.config import get_settings

require_scratch_database(get_settings().DATABASE_URL)

from app.database import async_session, engine


async def main() -> None:
    async with async_session() as s:
        for i, (status, hidden) in enumerate([
            ("published", False),
            ("published", True),
            ("unpublished", False),
            ("unpublished", True),
        ]):
            await s.execute(text(
                "INSERT INTO public.notes "
                "(id,slug,title,content,type,status,hidden,revision,ef,interval,repetitions) "
                "VALUES (gen_random_uuid(),:slug,'t','c','mistake',:status,:hidden,1,2.5,0,0)"
            ), {"slug": f"wk3fix-{i}", "status": status, "hidden": hidden})
        await s.commit()
        count = (await s.execute(
            text("SELECT count(*) FROM public.notes WHERE type='mistake'")
        )).scalar_one()
        print(f"SEEDED_LEGACY_MISTAKE_NOTES={count}")


asyncio.run(main())
