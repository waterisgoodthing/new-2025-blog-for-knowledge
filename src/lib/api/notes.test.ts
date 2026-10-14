import { describe, expect, it, vi } from 'vitest'
import {
  linkNoteKnowledgePoint,
  listKnowledgePointNotes,
  listNoteKnowledgePoints,
  unlinkNoteKnowledgePoint,
  type KnowledgePointNoteItem,
  type NoteKnowledgePointLink,
} from './notes'
import type { KnowledgePoint } from './taxonomy'

const NOTE_ID = '11111111-1111-1111-1111-111111111111'
const KP_ID = 7

const LINK_DTO_ALLOWLIST = ['note_id', 'knowledge_point_id', 'linked'] as const
const KP_NOTE_DTO_ALLOWLIST = ['id', 'slug', 'title', 'type', 'status', 'hidden'] as const

const linkFixture: NoteKnowledgePointLink = {
  note_id: NOTE_ID,
  knowledge_point_id: KP_ID,
  linked: true,
}

const kpNoteFixture: KnowledgePointNoteItem = {
  id: NOTE_ID,
  slug: 'csv-note',
  title: 'CSV 笔记',
  type: 'note',
  status: 'draft',
  hidden: false,
}

const knowledgePointFixture: KnowledgePoint = {
  id: KP_ID,
  subject_id: 2,
  parent_id: null,
  name: 'CSV 知识点',
  description: null,
  status: 'active',
  sort_order: 0,
  created_at: '2026-09-01T00:00:00Z',
  updated_at: '2026-09-02T00:00:00Z',
}

describe('Note <-> KnowledgePoint DTOs (PR-12)', () => {
  it('NoteKnowledgePointLink has exactly the backend schema fields', () => {
    expect(Object.keys(linkFixture).sort()).toEqual([...LINK_DTO_ALLOWLIST].sort())
  })

  it('KnowledgePointNoteItem has exactly the backend schema fields', () => {
    expect(Object.keys(kpNoteFixture).sort()).toEqual([...KP_NOTE_DTO_ALLOWLIST].sort())
  })
})

describe('linkNoteKnowledgePoint', () => {
  it('POSTs the admin link path with session credentials', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(linkFixture), { status: 200 }),
    )

    await expect(linkNoteKnowledgePoint(NOTE_ID, KP_ID)).resolves.toEqual(linkFixture)

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining(
        `/api/admin/notes/${NOTE_ID}/knowledge-points/${KP_ID}`,
      ),
      expect.objectContaining({ method: 'POST', credentials: 'include' }),
    )
    fetchMock.mockRestore()
  })
})

describe('unlinkNoteKnowledgePoint', () => {
  it('DELETEs the admin link path and resolves undefined on 204', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(null, { status: 204 }),
    )

    await expect(unlinkNoteKnowledgePoint(NOTE_ID, KP_ID)).resolves.toBeUndefined()

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining(
        `/api/admin/notes/${NOTE_ID}/knowledge-points/${KP_ID}`,
      ),
      expect.objectContaining({ method: 'DELETE', credentials: 'include' }),
    )
    fetchMock.mockRestore()
  })
})

describe('listNoteKnowledgePoints', () => {
  it('GETs the note -> knowledge-points admin path', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify([knowledgePointFixture]), { status: 200 }),
    )

    const response = await listNoteKnowledgePoints(NOTE_ID)
    expect(response).toEqual([knowledgePointFixture])

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining(`/api/admin/notes/${NOTE_ID}/knowledge-points`),
      expect.objectContaining({ credentials: 'include' }),
    )
    fetchMock.mockRestore()
  })
})

describe('listKnowledgePointNotes', () => {
  it('GETs the knowledge-point -> notes admin path', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify([kpNoteFixture]), { status: 200 }),
    )

    const response = await listKnowledgePointNotes(KP_ID)
    expect(response).toEqual([kpNoteFixture])

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining(
        `/api/admin/notes/knowledge-points/${KP_ID}/notes`,
      ),
      expect.objectContaining({ credentials: 'include' }),
    )
    fetchMock.mockRestore()
  })
})
