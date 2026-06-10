# Public Site Closure Upgrade

## Goal

Reframe the site around a complete public-user experience instead of an admin-first shell:

- anonymous visitors land on a coherent public-facing site, not management residue;
- the whole site forms a closed loop across public navigation, content consumption, interaction, and management feedback;
- public content boundaries are explicit for blog, notes, mistakes, discovery, and guest messages;
- management remains available, but is downgraded from the public primary navigation.

## Touched Domains

- `home`: public landing structure, distribution flow, and entry hierarchy.
- `manage`: anonymous `/manage` state becomes a public-facing entry page rather than a backend-looking shell.
- `blog`, `notes`, `mistakes`: public list/detail boundaries and cross-entity linking.
- `share`, `bloggers`: merged into a unified `discover` experience.
- `shared navigation`: desktop/mobile nav groups, labels, active states, and management demotion.
- `content infrastructure`: featured/starred discovery curation behavior.
- `new interaction domain`: guest message /留言 public flow and moderation/rate-limit path.

## Current Status

Approved for workflow construction on 2026-06-10.

This round remains documentation-only, but the task is no longer waiting for scope approval. The current state is:

- product direction approved in conversation;
- workflow documents created;
- closure review performed;
- follow-up doc fixes applied to align status, route strategy, and site-wide closure coverage;
- code implementation has not started yet.

This workflow captures the approved product direction before implementation:

- navigation groups become `公开内容` and `互动探索`;
- `推荐分享` and `优秀博客` merge into `发现`;
- `优秀笔记` joins the discovery system;
- blogs remain fully public;
- notes remain fully public;
- mistakes become limited public views;
- guest messages are anonymous but constrained by server-side abuse controls;
- the whole site must satisfy site-wide closure, not just page-local linking.

## Workflow Files

- [design.md](./design.md)
- [requirements.md](./requirements.md)
- [tasks.md](./tasks.md)
- [validation.md](./validation.md)
