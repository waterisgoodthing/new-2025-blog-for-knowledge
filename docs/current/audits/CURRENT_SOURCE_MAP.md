# 当前源码覆盖地图

日期：2026-10-09；AST静态抽取，不导入应用、不连接DB。所有行号对应本轮未改源码。模型声明不等于数据库实存，router decorators不等于权限穷尽或运行可达性，page文件可被redirect接管。

42 个ORM表声明、197 个router HTTP decorators、53 个page.tsx。FastAPI入口另有health；SQL-owned对象另见schema_manifest，不能由此表数推断完整schema。

## ORM模型

|表声明|类|证据|
|---|---|---|
|`admin_passwords`|`AdminPassword`|[backend/app/models/session.py](../../backend/app/models/session.py) L42|
|`admin_profiles`|`AdminProfile`|[backend/app/models/admin_profile.py](../../backend/app/models/admin_profile.py) L12|
|`admin_sessions`|`AdminSession`|[backend/app/models/session.py](../../backend/app/models/session.py) L12|
|`ai_call_logs`|`AiCallLog`|[backend/app/models/ai_call_log.py](../../backend/app/models/ai_call_log.py) L18|
|`ai_runs`|`AiRun`|[backend/app/models/ai_run.py](../../backend/app/models/ai_run.py) L14|
|`attachment_links`|`AttachmentLink`|[backend/app/models/attachment.py](../../backend/app/models/attachment.py) L69|
|`attachments`|`Attachment`|[backend/app/models/attachment.py](../../backend/app/models/attachment.py) L21|
|`attempts`|`Attempt`|[backend/app/models/attempt.py](../../backend/app/models/attempt.py) L12|
|`audit_logs`|`AuditLog`|[backend/app/models/audit.py](../../backend/app/models/audit.py) L12|
|`capture_items`|`CaptureItem`|[backend/app/models/capture.py](../../backend/app/models/capture.py) L28|
|`categories`|`Category`|[backend/app/models/note.py](../../backend/app/models/note.py) L107|
|`daily_songs`|`DailySong`|[backend/app/models/music_daily.py](../../backend/app/models/music_daily.py) L47|
|`draft_items`|`DraftItem`|[backend/app/models/question.py](../../backend/app/models/question.py) L32|
|`folders`|`Folder`|[backend/app/models/folder.py](../../backend/app/models/folder.py) L19|
|`guest_message_bans`|`GuestMessageBan`|[backend/app/models/guest_message.py](../../backend/app/models/guest_message.py) L36|
|`guest_messages`|`GuestMessage`|[backend/app/models/guest_message.py](../../backend/app/models/guest_message.py) L12|
|`knowledge_point_links`|`KnowledgePointLink`|[backend/app/models/taxonomy.py](../../backend/app/models/taxonomy.py) L67|
|`knowledge_points`|`KnowledgePoint`|[backend/app/models/taxonomy.py](../../backend/app/models/taxonomy.py) L10|
|`managed_content_entries`|`ManagedContentEntry`|[backend/app/models/content.py](../../backend/app/models/content.py) L10|
|`mistake_drafts`|`MistakeDraft`|[backend/app/models/mistake.py](../../backend/app/models/mistake.py) L12|
|`mistakes`|`Mistake`|[backend/app/models/mistake.py](../../backend/app/models/mistake.py) L63|
|`music_candidates`|`MusicCandidate`|[backend/app/models/music_daily.py](../../backend/app/models/music_daily.py) L24|
|`music_items`|`MusicItem`|[backend/app/models/music.py](../../backend/app/models/music.py) L10|
|`music_source_rules`|`MusicSourceRule`|[backend/app/models/music_daily.py](../../backend/app/models/music_daily.py) L12|
|`music_sync_logs`|`MusicSyncLog`|[backend/app/models/music_daily.py](../../backend/app/models/music_daily.py) L70|
|`netease_api_configs`|`NetEaseApiConfig`|[backend/app/models/music_daily.py](../../backend/app/models/music_daily.py) L88|
|`note_knowledge_points`|`NoteKnowledgePoint`|[backend/app/models/note_knowledge_point.py](../../backend/app/models/note_knowledge_point.py) L20|
|`note_links`|`NoteLink`|[backend/app/models/knowledge_markdown.py](../../backend/app/models/knowledge_markdown.py) L29|
|`note_versions`|`NoteVersion`|[backend/app/models/knowledge_markdown.py](../../backend/app/models/knowledge_markdown.py) L12|
|`notes`|`Note`|[backend/app/models/note.py](../../backend/app/models/note.py) L33|
|`passkey_credentials`|`PasskeyCredential`|[backend/app/models/session.py](../../backend/app/models/session.py) L30|
|`question_drafts`|`QuestionDraft`|[backend/app/models/question.py](../../backend/app/models/question.py) L87|
|`question_knowledge_points`|`QuestionKnowledgePoint`|[backend/app/models/question.py](../../backend/app/models/question.py) L206|
|`question_sources`|`QuestionSource`|[backend/app/models/question.py](../../backend/app/models/question.py) L181|
|`questions`|`Question`|[backend/app/models/question.py](../../backend/app/models/question.py) L130|
|`recommendations`|`DailyRecommendation`|[backend/app/models/recommendation.py](../../backend/app/models/recommendation.py) L10|
|`review_items`|`ReviewItem`|[backend/app/models/review_item.py](../../backend/app/models/review_item.py) L12|
|`review_records`|`ReviewRecord`|[backend/app/models/review_item.py](../../backend/app/models/review_item.py) L44|
|`subjects`|`Subject`|[backend/app/models/note.py](../../backend/app/models/note.py) L91|
|`tags`|`Tag`|[backend/app/models/note.py](../../backend/app/models/note.py) L82|
|`users`|`User`|[backend/app/models/note.py](../../backend/app/models/note.py) L115|
|`webauthn_challenges`|`WebAuthnChallenge`|[backend/app/models/webauthn_challenge.py](../../backend/app/models/webauthn_challenge.py) L12|

## 路由定义

router prefix与decorator直接合成；主入口注册与额外proxy/redirect需另查。此表不推断public/private；必须阅读对应dependency。

|Method|Path|证据|
|---|---|---|
|DELETE|`/api/admin/attachment-links/{link_id}`|[backend/app/routers/attachments.py](../../backend/app/routers/attachments.py) L129|
|DELETE|`/api/admin/attachments/{attachment_id}`|[backend/app/routers/attachments.py](../../backend/app/routers/attachments.py) L92|
|DELETE|`/api/admin/knowledge-points/{knowledge_point_id}`|[backend/app/routers/knowledge_points.py](../../backend/app/routers/knowledge_points.py) L97|
|DELETE|`/api/admin/mistakes/{mistake_id}`|[backend/app/routers/admin_mistakes.py](../../backend/app/routers/admin_mistakes.py) L106|
|DELETE|`/api/admin/notes/{note_id}/knowledge-points/{knowledge_point_id}`|[backend/app/routers/admin_notes.py](../../backend/app/routers/admin_notes.py) L103|
|DELETE|`/api/admin/questions/{question_id}`|[backend/app/routers/questions.py](../../backend/app/routers/questions.py) L93|
|DELETE|`/api/admin/subjects/{subject_id}`|[backend/app/routers/subjects.py](../../backend/app/routers/subjects.py) L63|
|DELETE|`/api/auth/sessions/{session_id}`|[backend/app/routers/auth.py](../../backend/app/routers/auth.py) L562|
|DELETE|`/api/categories/{category_id}`|[backend/app/routers/categories.py](../../backend/app/routers/categories.py) L51|
|DELETE|`/api/content/delete-image`|[backend/app/routers/content.py](../../backend/app/routers/content.py) L227|
|DELETE|`/api/folders/{folder_id}`|[backend/app/routers/folders.py](../../backend/app/routers/folders.py) L176|
|DELETE|`/api/music/items/{item_id}`|[backend/app/routers/music.py](../../backend/app/routers/music.py) L108|
|DELETE|`/api/music/manage/source-rules/{rule_id}`|[backend/app/routers/music_manage.py](../../backend/app/routers/music_manage.py) L172|
|DELETE|`/api/notes/{slug}`|[backend/app/routers/notes.py](../../backend/app/routers/notes.py) L420|
|DELETE|`/api/recommendations/today`|[backend/app/routers/recommendations.py](../../backend/app/routers/recommendations.py) L35|
|DELETE|`/api/tags/{tag_id}`|[backend/app/routers/tags.py](../../backend/app/routers/tags.py) L162|
|GET|`/api/admin/ai/runs`|[backend/app/routers/ai_runs.py](../../backend/app/routers/ai_runs.py) L32|
|GET|`/api/admin/ai/runs/{run_id}`|[backend/app/routers/ai_runs.py](../../backend/app/routers/ai_runs.py) L59|
|GET|`/api/admin/attachment-links`|[backend/app/routers/attachments.py](../../backend/app/routers/attachments.py) L103|
|GET|`/api/admin/attachments`|[backend/app/routers/attachments.py](../../backend/app/routers/attachments.py) L36|
|GET|`/api/admin/attachments/{attachment_id}`|[backend/app/routers/attachments.py](../../backend/app/routers/attachments.py) L62|
|GET|`/api/admin/attachments/{attachment_id}/content`|[backend/app/routers/attachments.py](../../backend/app/routers/attachments.py) L73|
|GET|`/api/admin/captures`|[backend/app/routers/captures.py](../../backend/app/routers/captures.py) L35|
|GET|`/api/admin/captures/{capture_id}`|[backend/app/routers/captures.py](../../backend/app/routers/captures.py) L57|
|GET|`/api/admin/dashboard/summary`|[backend/app/routers/dashboard.py](../../backend/app/routers/dashboard.py) L37|
|GET|`/api/admin/diagnostics`|[backend/app/routers/diagnostics.py](../../backend/app/routers/diagnostics.py) L20|
|GET|`/api/admin/drafts`|[backend/app/routers/drafts.py](../../backend/app/routers/drafts.py) L33|
|GET|`/api/admin/drafts/{draft_item_id}`|[backend/app/routers/drafts.py](../../backend/app/routers/drafts.py) L64|
|GET|`/api/admin/governance/summary`|[backend/app/routers/governance.py](../../backend/app/routers/governance.py) L13|
|GET|`/api/admin/knowledge-points`|[backend/app/routers/knowledge_points.py](../../backend/app/routers/knowledge_points.py) L33|
|GET|`/api/admin/knowledge-points/analytics`|[backend/app/routers/knowledge_points.py](../../backend/app/routers/knowledge_points.py) L48|
|GET|`/api/admin/knowledge-points/{knowledge_point_id}`|[backend/app/routers/knowledge_points.py](../../backend/app/routers/knowledge_points.py) L55|
|GET|`/api/admin/mistake-drafts`|[backend/app/routers/mistake_drafts.py](../../backend/app/routers/mistake_drafts.py) L33|
|GET|`/api/admin/mistake-drafts/{draft_item_id}`|[backend/app/routers/mistake_drafts.py](../../backend/app/routers/mistake_drafts.py) L60|
|GET|`/api/admin/mistakes`|[backend/app/routers/admin_mistakes.py](../../backend/app/routers/admin_mistakes.py) L58|
|GET|`/api/admin/mistakes/{mistake_id}`|[backend/app/routers/admin_mistakes.py](../../backend/app/routers/admin_mistakes.py) L66|
|GET|`/api/admin/notes/knowledge-points/{knowledge_point_id}/notes`|[backend/app/routers/admin_notes.py](../../backend/app/routers/admin_notes.py) L57|
|GET|`/api/admin/notes/{note_id}/knowledge-points`|[backend/app/routers/admin_notes.py](../../backend/app/routers/admin_notes.py) L71|
|GET|`/api/admin/practice/today`|[backend/app/routers/practice.py](../../backend/app/routers/practice.py) L16|
|GET|`/api/admin/profile`|[backend/app/routers/admin_profile.py](../../backend/app/routers/admin_profile.py) L13|
|GET|`/api/admin/questions`|[backend/app/routers/questions.py](../../backend/app/routers/questions.py) L28|
|GET|`/api/admin/questions/{question_id}`|[backend/app/routers/questions.py](../../backend/app/routers/questions.py) L58|
|GET|`/api/admin/review/items`|[backend/app/routers/review_items.py](../../backend/app/routers/review_items.py) L43|
|GET|`/api/admin/review/items/{item_id}/records`|[backend/app/routers/review_items.py](../../backend/app/routers/review_items.py) L56|
|GET|`/api/admin/subjects`|[backend/app/routers/subjects.py](../../backend/app/routers/subjects.py) L24|
|GET|`/api/admin/subjects/{subject_id}`|[backend/app/routers/subjects.py](../../backend/app/routers/subjects.py) L32|
|GET|`/api/admin/subjects/{subject_id}/knowledge-tree`|[backend/app/routers/subjects.py](../../backend/app/routers/subjects.py) L72|
|GET|`/api/admin/workspace/files`|[backend/app/routers/file_workspace.py](../../backend/app/routers/file_workspace.py) L38|
|GET|`/api/ai/call-logs`|[backend/app/routers/ai.py](../../backend/app/routers/ai.py) L419|
|GET|`/api/ai/call-logs/stats`|[backend/app/routers/ai.py](../../backend/app/routers/ai.py) L434|
|GET|`/api/ai/call-logs/usage-cost`|[backend/app/routers/ai.py](../../backend/app/routers/ai.py) L443|
|GET|`/api/ai/config`|[backend/app/routers/ai.py](../../backend/app/routers/ai.py) L78|
|GET|`/api/ai/prompts`|[backend/app/routers/ai.py](../../backend/app/routers/ai.py) L362|
|GET|`/api/ai/provider-health-snapshot`|[backend/app/routers/ai.py](../../backend/app/routers/ai.py) L410|
|GET|`/api/ai/provider-status`|[backend/app/routers/ai.py](../../backend/app/routers/ai.py) L403|
|GET|`/api/ai/suggestions`|[backend/app/routers/suggestions.py](../../backend/app/routers/suggestions.py) L28|
|GET|`/api/ai/weekly-summary`|[backend/app/routers/suggestions.py](../../backend/app/routers/suggestions.py) L112|
|GET|`/api/audit`|[backend/app/routers/audit.py](../../backend/app/routers/audit.py) L13|
|GET|`/api/auth/me`|[backend/app/routers/auth.py](../../backend/app/routers/auth.py) L516|
|GET|`/api/auth/passkey/auth-options`|[backend/app/routers/auth.py](../../backend/app/routers/auth.py) L331|
|GET|`/api/auth/passkey/status`|[backend/app/routers/auth.py](../../backend/app/routers/auth.py) L437|
|GET|`/api/auth/session-state`|[backend/app/routers/auth.py](../../backend/app/routers/auth.py) L528|
|GET|`/api/auth/sessions`|[backend/app/routers/auth.py](../../backend/app/routers/auth.py) L537|
|GET|`/api/categories`|[backend/app/routers/categories.py](../../backend/app/routers/categories.py) L13|
|GET|`/api/content/about`|[backend/app/routers/content.py](../../backend/app/routers/content.py) L74|
|GET|`/api/content/bloggers`|[backend/app/routers/content.py](../../backend/app/routers/content.py) L144|
|GET|`/api/content/pictures`|[backend/app/routers/content.py](../../backend/app/routers/content.py) L116|
|GET|`/api/content/projects`|[backend/app/routers/content.py](../../backend/app/routers/content.py) L102|
|GET|`/api/content/shares`|[backend/app/routers/content.py](../../backend/app/routers/content.py) L88|
|GET|`/api/content/site-settings`|[backend/app/routers/content.py](../../backend/app/routers/content.py) L158|
|GET|`/api/content/snippets`|[backend/app/routers/content.py](../../backend/app/routers/content.py) L130|
|GET|`/api/folders`|[backend/app/routers/folders.py](../../backend/app/routers/folders.py) L83|
|GET|`/api/guest-messages`|[backend/app/routers/guest_messages.py](../../backend/app/routers/guest_messages.py) L103|
|GET|`/api/guest-messages/bans`|[backend/app/routers/guest_messages.py](../../backend/app/routers/guest_messages.py) L160|
|GET|`/api/knowledge/weak-points`|[backend/app/routers/knowledge.py](../../backend/app/routers/knowledge.py) L33|
|GET|`/api/music/manage/candidates`|[backend/app/routers/music_manage.py](../../backend/app/routers/music_manage.py) L198|
|GET|`/api/music/manage/config`|[backend/app/routers/music_manage.py](../../backend/app/routers/music_manage.py) L101|
|GET|`/api/music/manage/daily-song`|[backend/app/routers/music_manage.py](../../backend/app/routers/music_manage.py) L213|
|GET|`/api/music/manage/daily-song/public`|[backend/app/routers/music_manage.py](../../backend/app/routers/music_manage.py) L282|
|GET|`/api/music/manage/diagnostics`|[backend/app/routers/music_manage.py](../../backend/app/routers/music_manage.py) L296|
|GET|`/api/music/manage/health`|[backend/app/routers/music_manage.py](../../backend/app/routers/music_manage.py) L129|
|GET|`/api/music/manage/history`|[backend/app/routers/music_manage.py](../../backend/app/routers/music_manage.py) L250|
|GET|`/api/music/manage/history/public`|[backend/app/routers/music_manage.py](../../backend/app/routers/music_manage.py) L288|
|GET|`/api/music/manage/source-rules`|[backend/app/routers/music_manage.py](../../backend/app/routers/music_manage.py) L145|
|GET|`/api/music/manage/sync-logs`|[backend/app/routers/music_manage.py](../../backend/app/routers/music_manage.py) L259|
|GET|`/api/music/playlist`|[backend/app/routers/music.py](../../backend/app/routers/music.py) L44|
|GET|`/api/notes`|[backend/app/routers/notes.py](../../backend/app/routers/notes.py) L58|
|GET|`/api/notes/{slug}`|[backend/app/routers/notes.py](../../backend/app/routers/notes.py) L221|
|GET|`/api/notes/{slug}/backlinks`|[backend/app/routers/notes.py](../../backend/app/routers/notes.py) L393|
|GET|`/api/notes/{slug}/versions`|[backend/app/routers/notes.py](../../backend/app/routers/notes.py) L381|
|GET|`/api/public/mistakes`|[backend/app/routers/public_mistakes.py](../../backend/app/routers/public_mistakes.py) L15|
|GET|`/api/recommendations/history`|[backend/app/routers/recommendations.py](../../backend/app/routers/recommendations.py) L46|
|GET|`/api/recommendations/today`|[backend/app/routers/recommendations.py](../../backend/app/routers/recommendations.py) L19|
|GET|`/api/review/plan`|[backend/app/routers/review.py](../../backend/app/routers/review.py) L101|
|GET|`/api/review/queue`|[backend/app/routers/review.py](../../backend/app/routers/review.py) L25|
|GET|`/api/review/stats`|[backend/app/routers/review.py](../../backend/app/routers/review.py) L79|
|GET|`/api/tags`|[backend/app/routers/tags.py](../../backend/app/routers/tags.py) L55|
|PATCH|`/api/admin/captures/{capture_id}`|[backend/app/routers/captures.py](../../backend/app/routers/captures.py) L68|
|PATCH|`/api/admin/mistakes/{mistake_id}/visibility`|[backend/app/routers/admin_mistakes.py](../../backend/app/routers/admin_mistakes.py) L89|
|PATCH|`/api/admin/questions/{question_id}`|[backend/app/routers/questions.py](../../backend/app/routers/questions.py) L81|
|PATCH|`/api/admin/workspace/files/{attachment_id}/move`|[backend/app/routers/file_workspace.py](../../backend/app/routers/file_workspace.py) L63|
|PATCH|`/api/admin/workspace/files/{attachment_id}/rename`|[backend/app/routers/file_workspace.py](../../backend/app/routers/file_workspace.py) L50|
|POST|`/api/admin/ai/runs/{run_id}/decision`|[backend/app/routers/ai_runs.py](../../backend/app/routers/ai_runs.py) L83|
|POST|`/api/admin/ai/runs/{run_id}/retry`|[backend/app/routers/ai_runs.py](../../backend/app/routers/ai_runs.py) L70|
|POST|`/api/admin/attachment-links`|[backend/app/routers/attachments.py](../../backend/app/routers/attachments.py) L118|
|POST|`/api/admin/attachments`|[backend/app/routers/attachments.py](../../backend/app/routers/attachments.py) L44|
|POST|`/api/admin/attempts`|[backend/app/routers/attempts.py](../../backend/app/routers/attempts.py) L13|
|POST|`/api/admin/attempts/review`|[backend/app/routers/attempts.py](../../backend/app/routers/attempts.py) L23|
|POST|`/api/admin/captures`|[backend/app/routers/captures.py](../../backend/app/routers/captures.py) L43|
|POST|`/api/admin/captures/{capture_id}/convert`|[backend/app/routers/captures.py](../../backend/app/routers/captures.py) L102|
|POST|`/api/admin/captures/{capture_id}/draft`|[backend/app/routers/captures.py](../../backend/app/routers/captures.py) L91|
|POST|`/api/admin/captures/{capture_id}/recognize`|[backend/app/routers/captures.py](../../backend/app/routers/captures.py) L80|
|POST|`/api/admin/drafts/questions`|[backend/app/routers/drafts.py](../../backend/app/routers/drafts.py) L44|
|POST|`/api/admin/drafts/{draft_item_id}/convert`|[backend/app/routers/drafts.py](../../backend/app/routers/drafts.py) L107|
|POST|`/api/admin/drafts/{draft_item_id}/reject`|[backend/app/routers/drafts.py](../../backend/app/routers/drafts.py) L91|
|POST|`/api/admin/knowledge-points`|[backend/app/routers/knowledge_points.py](../../backend/app/routers/knowledge_points.py) L66|
|POST|`/api/admin/knowledge-points/{knowledge_point_id}/archive`|[backend/app/routers/knowledge_points.py](../../backend/app/routers/knowledge_points.py) L114|
|POST|`/api/admin/mistake-drafts`|[backend/app/routers/mistake_drafts.py](../../backend/app/routers/mistake_drafts.py) L44|
|POST|`/api/admin/mistake-drafts/{draft_item_id}/convert`|[backend/app/routers/mistake_drafts.py](../../backend/app/routers/mistake_drafts.py) L99|
|POST|`/api/admin/mistake-drafts/{draft_item_id}/reject`|[backend/app/routers/mistake_drafts.py](../../backend/app/routers/mistake_drafts.py) L83|
|POST|`/api/admin/mistakes/ai-candidate`|[backend/app/routers/admin_mistakes.py](../../backend/app/routers/admin_mistakes.py) L136|
|POST|`/api/admin/mistakes/ai-confirm`|[backend/app/routers/admin_mistakes.py](../../backend/app/routers/admin_mistakes.py) L193|
|POST|`/api/admin/notes/{note_id}/knowledge-points/{knowledge_point_id}`|[backend/app/routers/admin_notes.py](../../backend/app/routers/admin_notes.py) L82|
|POST|`/api/admin/questions`|[backend/app/routers/questions.py](../../backend/app/routers/questions.py) L47|
|POST|`/api/admin/review/items/{item_id}/submit`|[backend/app/routers/review_items.py](../../backend/app/routers/review_items.py) L67|
|POST|`/api/admin/search`|[backend/app/routers/search.py](../../backend/app/routers/search.py) L13|
|POST|`/api/admin/subjects`|[backend/app/routers/subjects.py](../../backend/app/routers/subjects.py) L40|
|POST|`/api/admin/workspace/files/{attachment_id}/restore`|[backend/app/routers/file_workspace.py](../../backend/app/routers/file_workspace.py) L88|
|POST|`/api/admin/workspace/files/{attachment_id}/trash`|[backend/app/routers/file_workspace.py](../../backend/app/routers/file_workspace.py) L76|
|POST|`/api/ai/analyze`|[backend/app/routers/ai.py](../../backend/app/routers/ai.py) L85|
|POST|`/api/ai/analyze-stream`|[backend/app/routers/ai.py](../../backend/app/routers/ai.py) L159|
|POST|`/api/ai/analyze-text`|[backend/app/routers/ai.py](../../backend/app/routers/ai.py) L125|
|POST|`/api/ai/analyze-text-stream`|[backend/app/routers/ai.py](../../backend/app/routers/ai.py) L199|
|POST|`/api/ai/generate-knowledge-card`|[backend/app/routers/ai.py](../../backend/app/routers/ai.py) L275|
|POST|`/api/ai/generate-variant`|[backend/app/routers/ai.py](../../backend/app/routers/ai.py) L233|
|POST|`/api/ai/knowledge-summary`|[backend/app/routers/ai.py](../../backend/app/routers/ai.py) L315|
|POST|`/api/ai/mistake/diagram`|[backend/app/routers/ai.py](../../backend/app/routers/ai.py) L600|
|POST|`/api/ai/mistake/error-interpretation`|[backend/app/routers/ai.py](../../backend/app/routers/ai.py) L500|
|POST|`/api/ai/mistake/error-interpretation/reject`|[backend/app/routers/ai.py](../../backend/app/routers/ai.py) L533|
|POST|`/api/ai/mistake/final-analysis`|[backend/app/routers/ai.py](../../backend/app/routers/ai.py) L568|
|POST|`/api/ai/mistake/question-draft`|[backend/app/routers/ai.py](../../backend/app/routers/ai.py) L455|
|POST|`/api/ai/mistake/question-draft/confirm`|[backend/app/routers/ai.py](../../backend/app/routers/ai.py) L487|
|POST|`/api/ai/polish`|[backend/app/routers/ai_polish.py](../../backend/app/routers/ai_polish.py) L19|
|POST|`/api/ai/prompt-test`|[backend/app/routers/ai.py](../../backend/app/routers/ai.py) L369|
|POST|`/api/ai/suggestions/execute`|[backend/app/routers/suggestions.py](../../backend/app/routers/suggestions.py) L37|
|POST|`/api/ai/weekly-summary/generate`|[backend/app/routers/suggestions.py](../../backend/app/routers/suggestions.py) L165|
|POST|`/api/auth/login`|[backend/app/routers/auth.py](../../backend/app/routers/auth.py) L174|
|POST|`/api/auth/login-passkey`|[backend/app/routers/auth.py](../../backend/app/routers/auth.py) L256|
|POST|`/api/auth/logout`|[backend/app/routers/auth.py](../../backend/app/routers/auth.py) L445|
|POST|`/api/auth/passkey/operator/reg-options`|[backend/app/routers/auth.py](../../backend/app/routers/auth.py) L362|
|POST|`/api/auth/passkey/operator/register`|[backend/app/routers/auth.py](../../backend/app/routers/auth.py) L378|
|POST|`/api/auth/passkey/operator/validate-key`|[backend/app/routers/auth.py](../../backend/app/routers/auth.py) L354|
|POST|`/api/auth/register`|[backend/app/routers/auth.py](../../backend/app/routers/auth.py) L478|
|POST|`/api/auth/set-password`|[backend/app/routers/auth.py](../../backend/app/routers/auth.py) L589|
|POST|`/api/categories`|[backend/app/routers/categories.py](../../backend/app/routers/categories.py) L19|
|POST|`/api/content/upload-image`|[backend/app/routers/content.py](../../backend/app/routers/content.py) L172|
|POST|`/api/folders`|[backend/app/routers/folders.py](../../backend/app/routers/folders.py) L92|
|POST|`/api/folders/move-note/{slug}`|[backend/app/routers/folders.py](../../backend/app/routers/folders.py) L249|
|POST|`/api/folders/reorder`|[backend/app/routers/folders.py](../../backend/app/routers/folders.py) L227|
|POST|`/api/guest-messages`|[backend/app/routers/guest_messages.py](../../backend/app/routers/guest_messages.py) L76|
|POST|`/api/knowledge/context-pack`|[backend/app/routers/knowledge.py](../../backend/app/routers/knowledge.py) L17|
|POST|`/api/music/items`|[backend/app/routers/music.py](../../backend/app/routers/music.py) L52|
|POST|`/api/music/manage/generate-song`|[backend/app/routers/music_manage.py](../../backend/app/routers/music_manage.py) L222|
|POST|`/api/music/manage/source-rules`|[backend/app/routers/music_manage.py](../../backend/app/routers/music_manage.py) L153|
|POST|`/api/music/manage/sync`|[backend/app/routers/music_manage.py](../../backend/app/routers/music_manage.py) L181|
|POST|`/api/music/manage/sync/{rule_id}`|[backend/app/routers/music_manage.py](../../backend/app/routers/music_manage.py) L189|
|POST|`/api/notes`|[backend/app/routers/notes.py](../../backend/app/routers/notes.py) L243|
|POST|`/api/notes/batch-delete`|[backend/app/routers/notes.py](../../backend/app/routers/notes.py) L455|
|POST|`/api/notes/upload-image`|[backend/app/routers/notes.py](../../backend/app/routers/notes.py) L154|
|POST|`/api/notes/{slug}/promote`|[backend/app/routers/notes.py](../../backend/app/routers/notes.py) L471|
|POST|`/api/recommendations/today/generate`|[backend/app/routers/recommendations.py](../../backend/app/routers/recommendations.py) L27|
|POST|`/api/review/{slug}`|[backend/app/routers/review.py](../../backend/app/routers/review.py) L38|
|POST|`/api/tags`|[backend/app/routers/tags.py](../../backend/app/routers/tags.py) L61|
|POST|`/api/tags/{tag_id}/merge`|[backend/app/routers/tags.py](../../backend/app/routers/tags.py) L104|
|PUT|`/api/admin/drafts/{draft_item_id}`|[backend/app/routers/drafts.py](../../backend/app/routers/drafts.py) L75|
|PUT|`/api/admin/knowledge-points/{knowledge_point_id}`|[backend/app/routers/knowledge_points.py](../../backend/app/routers/knowledge_points.py) L81|
|PUT|`/api/admin/mistake-drafts/{draft_item_id}`|[backend/app/routers/mistake_drafts.py](../../backend/app/routers/mistake_drafts.py) L71|
|PUT|`/api/admin/mistakes/{mistake_id}`|[backend/app/routers/admin_mistakes.py](../../backend/app/routers/admin_mistakes.py) L77|
|PUT|`/api/admin/profile`|[backend/app/routers/admin_profile.py](../../backend/app/routers/admin_profile.py) L24|
|PUT|`/api/admin/questions/{question_id}`|[backend/app/routers/questions.py](../../backend/app/routers/questions.py) L69|
|PUT|`/api/admin/subjects/{subject_id}`|[backend/app/routers/subjects.py](../../backend/app/routers/subjects.py) L51|
|PUT|`/api/categories/{category_id}`|[backend/app/routers/categories.py](../../backend/app/routers/categories.py) L31|
|PUT|`/api/content/about`|[backend/app/routers/content.py](../../backend/app/routers/content.py) L79|
|PUT|`/api/content/bloggers`|[backend/app/routers/content.py](../../backend/app/routers/content.py) L149|
|PUT|`/api/content/pictures`|[backend/app/routers/content.py](../../backend/app/routers/content.py) L121|
|PUT|`/api/content/projects`|[backend/app/routers/content.py](../../backend/app/routers/content.py) L107|
|PUT|`/api/content/shares`|[backend/app/routers/content.py](../../backend/app/routers/content.py) L93|
|PUT|`/api/content/site-settings`|[backend/app/routers/content.py](../../backend/app/routers/content.py) L163|
|PUT|`/api/content/snippets`|[backend/app/routers/content.py](../../backend/app/routers/content.py) L135|
|PUT|`/api/folders/{folder_id}`|[backend/app/routers/folders.py](../../backend/app/routers/folders.py) L132|
|PUT|`/api/guest-messages/{message_id}/moderate`|[backend/app/routers/guest_messages.py](../../backend/app/routers/guest_messages.py) L136|
|PUT|`/api/music/items/{item_id}`|[backend/app/routers/music.py](../../backend/app/routers/music.py) L82|
|PUT|`/api/music/manage/config`|[backend/app/routers/music_manage.py](../../backend/app/routers/music_manage.py) L120|
|PUT|`/api/music/manage/local-selection`|[backend/app/routers/music_manage.py](../../backend/app/routers/music_manage.py) L233|
|PUT|`/api/music/manage/source-rules/{rule_id}`|[backend/app/routers/music_manage.py](../../backend/app/routers/music_manage.py) L162|
|PUT|`/api/notes/{slug}`|[backend/app/routers/notes.py](../../backend/app/routers/notes.py) L320|
|PUT|`/api/tags/{tag_id}`|[backend/app/routers/tags.py](../../backend/app/routers/tags.py) L74|

## 前端页面

|页面文件|
|---|
|[src/app/(home)/page.tsx](<../../src/app/(home)/page.tsx>)|
|[src/app/about/page.tsx](<../../src/app/about/page.tsx>)|
|[src/app/blog/[id]/page.tsx](<../../src/app/blog/[id]/page.tsx>)|
|[src/app/blog/page.tsx](<../../src/app/blog/page.tsx>)|
|[src/app/bloggers/page.tsx](<../../src/app/bloggers/page.tsx>)|
|[src/app/clock/page.tsx](<../../src/app/clock/page.tsx>)|
|[src/app/discover/page.tsx](<../../src/app/discover/page.tsx>)|
|[src/app/guestbook/page.tsx](<../../src/app/guestbook/page.tsx>)|
|[src/app/image-toolbox/page.tsx](<../../src/app/image-toolbox/page.tsx>)|
|[src/app/live2d/page.tsx](<../../src/app/live2d/page.tsx>)|
|[src/app/manage/(workspace)/ai/page.tsx](<../../src/app/manage/(workspace)/ai/page.tsx>)|
|[src/app/manage/(workspace)/ai/runs/page.tsx](<../../src/app/manage/(workspace)/ai/runs/page.tsx>)|
|[src/app/manage/(workspace)/analytics/page.tsx](<../../src/app/manage/(workspace)/analytics/page.tsx>)|
|[src/app/manage/(workspace)/attachments/[id]/page.tsx](<../../src/app/manage/(workspace)/attachments/[id]/page.tsx>)|
|[src/app/manage/(workspace)/attachments/page.tsx](<../../src/app/manage/(workspace)/attachments/page.tsx>)|
|[src/app/manage/(workspace)/capture/page.tsx](<../../src/app/manage/(workspace)/capture/page.tsx>)|
|[src/app/manage/(workspace)/dashboard/page.tsx](<../../src/app/manage/(workspace)/dashboard/page.tsx>)|
|[src/app/manage/(workspace)/drafts/[id]/page.tsx](<../../src/app/manage/(workspace)/drafts/[id]/page.tsx>)|
|[src/app/manage/(workspace)/drafts/page.tsx](<../../src/app/manage/(workspace)/drafts/page.tsx>)|
|[src/app/manage/(workspace)/jobs/page.tsx](<../../src/app/manage/(workspace)/jobs/page.tsx>)|
|[src/app/manage/(workspace)/knowledge-points/[id]/page.tsx](<../../src/app/manage/(workspace)/knowledge-points/[id]/page.tsx>)|
|[src/app/manage/(workspace)/knowledge-points/page.tsx](<../../src/app/manage/(workspace)/knowledge-points/page.tsx>)|
|[src/app/manage/(workspace)/mistakes/[id]/page.tsx](<../../src/app/manage/(workspace)/mistakes/[id]/page.tsx>)|
|[src/app/manage/(workspace)/mistakes/page.tsx](<../../src/app/manage/(workspace)/mistakes/page.tsx>)|
|[src/app/manage/(workspace)/notes/[slug]/page.tsx](<../../src/app/manage/(workspace)/notes/[slug]/page.tsx>)|
|[src/app/manage/(workspace)/notes/new/page.tsx](<../../src/app/manage/(workspace)/notes/new/page.tsx>)|
|[src/app/manage/(workspace)/notes/page.tsx](<../../src/app/manage/(workspace)/notes/page.tsx>)|
|[src/app/manage/(workspace)/practice/page.tsx](<../../src/app/manage/(workspace)/practice/page.tsx>)|
|[src/app/manage/(workspace)/questions/[id]/page.tsx](<../../src/app/manage/(workspace)/questions/[id]/page.tsx>)|
|[src/app/manage/(workspace)/questions/page.tsx](<../../src/app/manage/(workspace)/questions/page.tsx>)|
|[src/app/manage/(workspace)/review/page.tsx](<../../src/app/manage/(workspace)/review/page.tsx>)|
|[src/app/manage/(workspace)/search/page.tsx](<../../src/app/manage/(workspace)/search/page.tsx>)|
|[src/app/manage/(workspace)/settings/page.tsx](<../../src/app/manage/(workspace)/settings/page.tsx>)|
|[src/app/manage/(workspace)/subjects/[id]/page.tsx](<../../src/app/manage/(workspace)/subjects/[id]/page.tsx>)|
|[src/app/manage/(workspace)/subjects/page.tsx](<../../src/app/manage/(workspace)/subjects/page.tsx>)|
|[src/app/manage/page.tsx](<../../src/app/manage/page.tsx>)|
|[src/app/mistakes/page.tsx](<../../src/app/mistakes/page.tsx>)|
|[src/app/mistakes/review/page.tsx](<../../src/app/mistakes/review/page.tsx>)|
|[src/app/music/page.tsx](<../../src/app/music/page.tsx>)|
|[src/app/notes/[id]/page.tsx](<../../src/app/notes/[id]/page.tsx>)|
|[src/app/notes/page.tsx](<../../src/app/notes/page.tsx>)|
|[src/app/pictures/page.tsx](<../../src/app/pictures/page.tsx>)|
|[src/app/projects/page.tsx](<../../src/app/projects/page.tsx>)|
|[src/app/share/page.tsx](<../../src/app/share/page.tsx>)|
|[src/app/snippets/page.tsx](<../../src/app/snippets/page.tsx>)|
|[src/app/svgs/page.tsx](<../../src/app/svgs/page.tsx>)|
|[src/app/write-mistake/[slug]/page.tsx](<../../src/app/write-mistake/[slug]/page.tsx>)|
|[src/app/write-mistake/page.tsx](<../../src/app/write-mistake/page.tsx>)|
|[src/app/write-note/[slug]/page.tsx](<../../src/app/write-note/[slug]/page.tsx>)|
|[src/app/write-note/page.tsx](<../../src/app/write-note/page.tsx>)|
|[src/app/write/[slug]/page.tsx](<../../src/app/write/[slug]/page.tsx>)|
|[src/app/write/page.tsx](<../../src/app/write/page.tsx>)|
|[src/app/wuthering-waves/page.tsx](<../../src/app/wuthering-waves/page.tsx>)|

## schema与源码权威

- Alembic AST：36 revisions；唯一head034，无缺失parent。
- `backend/main.py` expected034；`backend/app/models/schema_manifest.json` revision034。
- ORM lifecycle registry、SQL-owned allowlist、catalog definition manifest是分开的治理来源，CI需运行两门禁；本轮仅验证定义/图，不运行数据库。
- 安全、业务和未来目标的裁决见 [审查](ARCHITECTURE_AUDIT.md)。
