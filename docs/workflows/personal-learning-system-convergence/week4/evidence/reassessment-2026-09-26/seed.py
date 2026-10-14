import asyncio
from app.database import async_session,engine
from app.cli import bootstrap_temp_admin
async def main():
    async with async_session() as db:
        await bootstrap_temp_admin(db,username='ci-admin',password='ci-test-admin-password')
        await db.commit()
    await engine.dispose()
asyncio.run(main())
print('test admin seeded')
