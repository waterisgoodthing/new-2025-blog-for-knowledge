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

All phases implemented on 2026-06-10.

- product direction approved in conversation;
- workflow documents created;
- closure review performed;
- follow-up doc fixes applied;
- Phase 0 (scope lock): confirmed;
- Phase 1 (shared navigation): implemented in `vertical-nav.tsx`, `mobile-nav.tsx`, `nav-card.tsx`, `share-card.tsx`;
- Phase 2 (manage anonymous experience): redesigned `LoginForm` in `manage/page.tsx`;
- Phase 3 (public content boundaries): admin-gated buttons in blog/note detail, limited public mistake view;
- Phase 4 (discover system merge): new `/discover` page, legacy route redirects for non-admin;
- Phase 5 (guest message domain): backend model/schema/router + frontend `/guestbook` page;
- Phase 6 (site-wide closure pass): closure links added to about, discover, guestbook, and content detail pages;
- Phase 7 (validation): `npx tsc --noEmit` passes, backend imports verified, browser validation pending.

## Workflow Files

- [design.md](./design.md)
- [requirements.md](./requirements.md)
- [tasks.md](./tasks.md)
- [validation.md](./validation.md)
