# UI Page Inventory

Review date: 2026-07-19. Frontend discovered from `src/app/**/page.tsx`; evidence comes from a real Chromium browser against `http://localhost:2025`.

| Route | Access observed | Desktop / mobile | Screenshot | Console / network |
| -- | -- | -- | -- | -- |
| `/`, `/about`, `/blog`, `/bloggers`, `/clock`, `/discover`, `/guestbook`, `/image-toolbox`, `/live2d` | HTTP 200; rendered but globally unstyled | Reviewed at 1440x900 and 390x844; `/` also 1280x800 | Complete | Failed CSS/JS chunks on every capture |
| `/mistakes`, `/music`, `/notes`, `/pictures`, `/projects`, `/share`, `/snippets`, `/svgs`, `/wuthering-waves` | HTTP 200; rendered but globally unstyled | Reviewed at 1440x900 and 390x844; selected routes at 1280x800 | Complete | Failed CSS/JS chunks on every capture |
| `/manage` | Password login succeeded with user-authorized local temporary account; legacy manager rendered | Reviewed at 1440x900 and 390x844 | Complete | Healthy on fresh local instance; mobile table is not responsive |
| `/manage/dashboard`, `/manage/questions`, `/manage/mistakes`, `/manage/review`, `/manage/ai/runs` | Authenticated workspace rendered | Desktop coverage for all; mobile coverage for first four | Complete | No application asset failure on fresh instance; initial anonymous `/api/auth/me` 401 expected |
| `/mistakes/review`, `/write`, `/write-mistake`, `/write-note` | Anonymous state observed only | Reviewed at 1440x900 and 390x844 | Complete | No login state follow-up for these legacy routes |
| `/blog/[id]`, `/notes/[id]`, `/write/[slug]`, `/write-mistake/[slug]`, `/write-note/[slug]` | Dynamic identifier unavailable or login-protected | Not covered | No | No safe test identifier / no test credentials supplied |
| `/manage/ai`, `/manage/ai/runs`, `/manage/analytics`, `/manage/attachments`, `/manage/attachments/[id]`, `/manage/capture`, `/manage/dashboard`, `/manage/drafts`, `/manage/drafts/[id]`, `/manage/jobs`, `/manage/knowledge-points`, `/manage/knowledge-points/[id]`, `/manage/mistakes`, `/manage/mistakes/[id]`, `/manage/questions`, `/manage/questions/[id]`, `/manage/review`, `/manage/search`, `/manage/settings`, `/manage/subjects`, `/manage/subjects/[id]` | Management workspace; login required | Not covered | No | Authentication boundary preserved; no bypass used |

Result: 43 route modules discovered. 23 directly addressable routes were browser-rendered at both required desktop and mobile viewports; 6 representative routes were also rendered at the laptop viewport. The inherited `localhost:2025` instance had static-resource failures; a fresh independent `localhost:3000` instance served healthy assets for five public routes and the authenticated management follow-up.
