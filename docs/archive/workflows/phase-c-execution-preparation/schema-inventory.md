# Schema Inventory

日期：2026-07-13  
来源：当前 PostgreSQL `information_schema`、`pg_indexes`、`pg_constraint` 只读查询。字段标记 `NN` = NOT NULL，`NULL` = nullable。

## 核心表覆盖

数据库中用户要求的 13 个核心表全部存在：`notes`、`questions`、`mistakes`、`mistake_drafts`、`review_items`、`review_records`、`knowledge_points`、`knowledge_point_links`、`managed_content_entries`、`attachments`、`attachment_links`、`ai_runs`、`ai_call_logs`。

## 表结构

### notes

```text
columns: id uuid NN; slug varchar NN; title varchar NN; content text NN; type varchar NN; hidden bool NN; created_at timestamp NN; updated_at timestamp NN; summary text NULL; cover varchar NULL; category varchar NULL; subject varchar NULL; difficulty varchar NULL; question text NULL; my_answer text NULL; correct_answer text NULL; analysis text NULL; knowledge_points text NULL; ef float8 NN; interval int4 NN; repetitions int4 NN; next_review date NULL; last_reviewed timestamp NULL; search_vector tsvector NULL; status varchar NN; images json NULL; ai_metadata json NULL; folder_id uuid NULL; sort_order int4 NULL
indexes: notes_pkey; ix_notes_slug UNIQUE; ix_notes_type; idx_notes_status; idx_notes_next_review (partial type='mistake'); idx_notes_search GIN(search_vector); idx_notes_folder_id
foreign keys: notes_folder_id_fkey (folder_id -> folders.id, ON DELETE SET NULL)
constraints: notes_pkey PRIMARY KEY(id)
```

### questions

```text
columns: id uuid NN; subject_id int4 NN; title varchar NULL; question_text text NN; question_type varchar NN; options json NN; correct_answer text NULL; explanation text NULL; difficulty varchar NULL; status varchar NN; visibility varchar NN; version int4 NN; created_at timestamptz NN; updated_at timestamptz NN
indexes: questions_pkey; idx_questions_subject_status; idx_questions_updated
foreign keys: fk_questions_subject (subject_id -> subjects.id, ON DELETE RESTRICT)
constraints: ck_questions_difficulty; ck_questions_status; ck_questions_type; ck_questions_version; ck_questions_visibility; questions_pkey PRIMARY KEY(id)
```

### mistakes

```text
columns: id uuid NN; source_draft_item_id uuid NN; question_id uuid NN; subject_id int4 NN; title varchar NULL; question_text text NN; my_answer text NULL; correct_answer text NULL; analysis text NULL; reason_category varchar NN; mistake_reason text NULL; difficulty varchar NULL; status varchar NN; visibility varchar NN; version int4 NN; created_at timestamptz NN; updated_at timestamptz NN
indexes: mistakes_pkey; idx_mistakes_subject_status; mistakes_source_draft_item_id_key UNIQUE
foreign keys: question_id -> questions.id RESTRICT; source_draft_item_id -> draft_items.id RESTRICT; subject_id -> subjects.id RESTRICT
constraints: ck_mistakes_status; ck_mistakes_version; ck_mistakes_visibility; mistakes_source_draft_item_id_key UNIQUE(source_draft_item_id); mistakes_pkey PRIMARY KEY(id)
```

### mistake_drafts

```text
columns: id uuid NN; draft_item_id uuid NN; question_id uuid NULL; question_draft_id uuid NULL; subject_id int4 NN; title varchar NULL; question_text text NN; my_answer text NULL; correct_answer_snapshot text NULL; explanation_snapshot text NULL; reason_category varchar NN; mistake_reason text NULL; difficulty varchar NULL; created_at timestamptz NN; updated_at timestamptz NN
indexes: mistake_drafts_pkey; idx_mistake_drafts_subject; mistake_drafts_draft_item_id_key UNIQUE
foreign keys: draft_item_id -> draft_items.id CASCADE; question_id -> questions.id RESTRICT; question_draft_id -> question_drafts.id RESTRICT; subject_id -> subjects.id RESTRICT
constraints: ck_mistake_drafts_difficulty; ck_mistake_drafts_question_source; ck_mistake_drafts_reason_category; UNIQUE(draft_item_id); PRIMARY KEY(id)
```

### review_items

```text
columns: id uuid NN; target_type varchar NN; target_id varchar NN; state varchar NN; algorithm varchar NN; interval_days int4 NN; repetitions int4 NN; next_review_at timestamptz NN; last_reviewed_at timestamptz NULL; created_at timestamptz NN; updated_at timestamptz NN
indexes: review_items_pkey; idx_review_items_due; uq_review_items_target UNIQUE
foreign keys: none; target_id is polymorphic and has no database FK
constraints: ck_review_items_algorithm; ck_review_items_counts; ck_review_items_state; ck_review_items_target_type; UNIQUE(target_type,target_id); PRIMARY KEY(id)
```

### review_records

```text
columns: id uuid NN; review_item_id uuid NN; rating int4 NN; reviewed_at timestamptz NN; previous_interval_days int4 NN; next_interval_days int4 NN; previous_next_review_at timestamptz NN; next_review_at timestamptz NN; created_at timestamptz NN
indexes: review_records_pkey; idx_review_records_item_time
foreign keys: review_item_id -> review_items.id RESTRICT
constraints: ck_review_records_intervals; ck_review_records_rating; PRIMARY KEY(id)
```

### knowledge_points

```text
columns: id int4 NN; subject_id int4 NN; chapter_id int4 NULL; name varchar NN; description text NULL; sort_order int4 NN; is_active bool NN; created_at timestamptz NN; updated_at timestamptz NN
indexes: knowledge_points_pkey; idx_knowledge_points_chapter; idx_knowledge_points_subject_sort; uq_knowledge_points_subject_name UNIQUE
foreign keys: subject_id -> subjects.id CASCADE; chapter_id -> chapters.id SET NULL
constraints: UNIQUE(subject_id,name); PRIMARY KEY(id)
```

### knowledge_point_links

```text
columns: id int4 NN; knowledge_point_id int4 NN; target_type varchar NN; target_id varchar NN; created_at timestamptz NN
indexes: knowledge_point_links_pkey; idx_knowledge_point_links_target; uq_knowledge_point_links_target UNIQUE
foreign keys: knowledge_point_id -> knowledge_points.id CASCADE; target_id is polymorphic and has no database FK
constraints: UNIQUE(knowledge_point_id,target_type,target_id); PRIMARY KEY(id)
```

### managed_content_entries

```text
columns: key varchar NN; data json NN; created_at timestamptz NN; updated_at timestamptz NN
indexes: managed_content_entries_pkey
foreign keys: none
constraints: PRIMARY KEY(key)
```

### attachments

```text
columns: id uuid NN; original_name varchar NN; storage_provider varchar NN; storage_key varchar NN; mime_type varchar NN; size_bytes int4 NN; checksum_sha256 varchar NN; visibility varchar NN; status varchar NN; created_by uuid NULL; created_at timestamptz NN; updated_at timestamptz NN; deleted_at timestamptz NULL
indexes: attachments_pkey; attachments_storage_key_key UNIQUE; idx_attachments_checksum; idx_attachments_status_created
foreign keys: created_by -> users.id SET NULL
constraints: ck_attachments_checksum; ck_attachments_size; ck_attachments_status; ck_attachments_storage_provider; ck_attachments_visibility; UNIQUE(storage_key); PRIMARY KEY(id)
```

### attachment_links

```text
columns: id uuid NN; attachment_id uuid NN; target_type varchar NN; target_id varchar NN; purpose varchar NN; sort_order int4 NN; created_at timestamptz NN
indexes: attachment_links_pkey; idx_attachment_links_attachment; idx_attachment_links_target; uq_attachment_links_target_purpose UNIQUE
foreign keys: attachment_id -> attachments.id CASCADE; target_id is polymorphic and has no database FK
constraints: ck_attachment_links_purpose; ck_attachment_links_target_type; UNIQUE(attachment_id,target_type,target_id,purpose); PRIMARY KEY(id)
```

### ai_runs

```text
columns: id uuid NN; task_type varchar NN; target_type varchar NULL; target_id varchar NULL; provider_used varchar NULL; model varchar NULL; prompt_version varchar NULL; status varchar NN; validation_status varchar NN; input_summary text NULL; replay_input json NULL; output_data json NULL; warnings json NULL; error_code varchar NULL; error_message_safe text NULL; attempt int4 NN; parent_run_id uuid NULL; review_status varchar NN; review_revision int4 NN; reviewed_at timestamptz NULL; review_note text NULL; latency_ms int4 NULL; started_at timestamptz NN; finished_at timestamptz NULL; created_at timestamptz NN; updated_at timestamptz NN
indexes: ai_runs_pkey; idx_ai_runs_created_at; idx_ai_runs_parent_run_id; idx_ai_runs_review_status; idx_ai_runs_status; idx_ai_runs_task_type
foreign keys: parent_run_id -> ai_runs.id SET NULL; target_id is polymorphic and has no database FK
constraints: ck_ai_runs_attempt; ck_ai_runs_parent_not_self; ck_ai_runs_review_status; ck_ai_runs_status; ck_ai_runs_validation_status; PRIMARY KEY(id)
```

### ai_call_logs

```text
columns: id uuid NN; task_type varchar NN; provider_used varchar NN; model varchar NN; latency_ms int4 NN; success bool NN; error text NULL; fallback_used bool NN; attempts json NULL; input_summary text NULL; created_at timestamptz NN; prompt_version varchar NULL
indexes: ai_call_logs_pkey; idx_ai_call_logs_created_at; idx_ai_call_logs_success; idx_ai_call_logs_task_type
foreign keys: none; no ai_run_id FK present
constraints: PRIMARY KEY(id)
```

## Inventory risks

- `review_items.target_id`、`knowledge_point_links.target_id`、`attachment_links.target_id` 与 `ai_runs.target_id` 为多态字符串，无真实 FK，必须依赖应用层完整性与 owner 校验。
- `attachments.created_by` 是 nullable 操作者字段，不是 owner contract。
- `ai_call_logs` 没有 `ai_run_id` 或 owner 字段，不能仅凭调用日志推断业务归属。
- `notes` 仍同时承载错题字段、复习字段、`images` 与 `ai_metadata`，与独立实体并存。
