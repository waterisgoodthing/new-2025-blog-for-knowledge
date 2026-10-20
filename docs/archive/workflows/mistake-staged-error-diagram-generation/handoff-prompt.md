# Handoff Prompt

Implement `mistake-staged-error-diagram-generation` in `/Users/limengyang/2025-blog-public`.

Rules:

- Read `AGENTS.md` first.
- Start with `git status --short`.
- Do not implement until `tasks.md` has been explicitly approved in conversation.
- Execute one task at a time.
- Update `tasks.md` immediately after each completed task.
- Keep AI question extraction separate from learner error-reason interpretation.
- Do not allow AI to replace learner-written error reason with option-based guessing.
- Prefer structured diagrams over image generation.
- Use Qwen image generation only as fallback, model `qwen-image-2.0-pro`.
- Record validation in `validation.md`.
