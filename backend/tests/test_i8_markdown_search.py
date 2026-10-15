import unittest
import uuid

from sqlalchemy import select

from app.database import async_session, engine
from app.models.note import Note
from app.services.knowledge_markdown_service import (
    SearchQuery,
    create_initial_version,
    list_backlinks,
    list_note_versions,
    search_notes,
    sync_wikilinks,
)


class MarkdownSearchServiceTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.session = async_session()
        self.addAsyncCleanup(engine.dispose)
        self.addAsyncCleanup(self.session.close)
        self.addAsyncCleanup(self.session.rollback)
        await self.session.begin()

    async def test_initial_version_and_wikilink_backlink_use_stable_note_id(self):
        suffix = uuid.uuid4().hex[:8]
        target = Note(slug=f"target-{suffix}", title="Target", content="stable target", type="note")
        source = Note(
            slug=f"source-{suffix}",
            title="Source",
            content=f"See [[{target.slug}]]",
            type="note",
        )
        self.session.add_all([target, source])
        await self.session.flush()

        await create_initial_version(self.session, source)
        await sync_wikilinks(self.session, source)

        versions = await list_note_versions(self.session, source.id)
        backlinks = await list_backlinks(self.session, target.id)
        self.assertEqual(len(versions), 1)
        self.assertEqual(versions[0].version, 1)
        self.assertEqual([item.source_note_id for item in backlinks], [source.id])

    async def test_search_returns_real_notes_and_empty_query_is_empty(self):
        suffix = uuid.uuid4().hex[:8]
        visible = Note(slug=f"visible-{suffix}", title="Trigram Networking", content="window protocol", type="note", status="published", hidden=False)
        hidden = Note(slug=f"hidden-{suffix}", title="Trigram Secret", content="private protocol", type="note", status="draft", hidden=True)
        self.session.add_all([visible, hidden])
        await self.session.flush()

        self.assertEqual(await search_notes(self.session, SearchQuery(query="")), [])
        results = await search_notes(self.session, SearchQuery(query="Trigram"))
        self.assertIn(visible.id, [item.id for item in results])
        self.assertNotIn(hidden.id, [item.id for item in results])
