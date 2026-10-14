# Week 3 Gate — migration replay evidence (030→032)

agent_id: GATE-seed-verify  date: 2026-09-25
DB: astra_week3_gate_mig (fresh, guarded)

| Step | Command | Result | Log |
|---|---|---|---|
| upgrade 030 | alembic upgrade 030 | 032 migrations applied, current=030 | gate-mig-upgrade-030.log |
| upgrade 030→032 | alembic upgrade 032 | 030→031 (visibility widen), 031→032 (Note↔KP) applied; current=032 | gate-mig-upgrade-032.log |
| downgrade 032→030 | alembic downgrade 030 | 032→031, 031→030 downgraded; current=030 | gate-mig-downgrade-032-030.log |
| re-upgrade head | alembic upgrade head | back to 032 (head), single head | gate-mig-reupgrade-head.log |
| heads | alembic heads | single head `032` | (in reupgrade log) |

## Schema/integrity queries (gate-mig-schema-shapes.txt)
- `note_knowledge_points` columns: note_id uuid NOT NULL (PK), knowledge_point_id integer NOT NULL (PK), created_at timestamptz — matches W3-D04.
- Constraints:
  - `note_knowledge_points_pkey` PRIMARY KEY (note_id, knowledge_point_id)
  - `fk_note_knowledge_points_note_id` FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
  - `fk_note_knowledge_points_knowledge_point_id` FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id) ON DELETE CASCADE
- `ck_mistakes_visibility` CHECK allows ('private','public').

## Downgrade fail-closed with public rows
Already proven in PR-09 acceptance: `pr-09-db-migration-a3-downgrade-with-public-FAIL-EXPECTED.log` —
RuntimeError "re-narrowing ck_mistakes_visibility to private-only would violate data" when 1 public row exists.
Referred, not re-run (identical migration 031 downgrade code).

## Duplicate/FK rejection at DB level (Q5 evidence, gate-q5.json)
- raw duplicate composite-PK INSERT into note_knowledge_points → IntegrityError (duplicate key)
- raw INSERT with nonexistent note_id → IntegrityError (foreign key)