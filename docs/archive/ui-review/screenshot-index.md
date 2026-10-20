# Screenshot Index

All screenshots are genuine Chromium captures from `http://localhost:2025`. Names follow `<page>-<viewport>-<state>.png`; each route below has both `first` (viewport) and `full` capture unless marked otherwise.

| Directory / file pattern | Routes | Viewport | State / focus |
| -- | -- | -- | -- |
| `artifacts/desktop/{home,about,blog,bloggers,clock,discover,guestbook,image-toolbox,live2d,manage,mistakes,mistakes-review,music,notes,pictures,projects,share,snippets,svgs,wuthering-waves,write,write-mistake,write-note}-1440x900-{first,full}.png` | 23 directly addressable routes | 1440x900 | Full desktop coverage; look for raw blue SVGs / missing style layer |
| `artifacts/laptop/{home,blog,notes,mistakes,music,manage}-1280x800-{first,full}.png` | Representative home, content, data, and management surfaces | 1280x800 | Laptop coverage; same chunk failures |
| `artifacts/mobile/{home,about,blog,bloggers,clock,discover,guestbook,image-toolbox,live2d,manage,mistakes,mistakes-review,music,notes,pictures,projects,share,snippets,svgs,wuthering-waves,write,write-mistake,write-note}-390x844-{first,full}.png` | 23 directly addressable routes | 390x844 | Full mobile coverage; navigation/control layout is unusable without CSS |
| `artifacts/states/home-390x844-first-button-state.png` | `/` | 390x844 | First visible button interaction attempt; retained as state evidence |
| `artifacts/browser-observations-*.json` | Reviewed route/viewport observations | All | Raw browser facts: URL/status, document dimensions, text, console entries, failed requests, and >=400 responses |
| `artifacts/authenticated/manage-1440x900-{login,authenticated}.png` | `/manage` | 1440x900 | Login and authenticated legacy manager |
| `artifacts/authenticated/manage-{dashboard,questions,mistakes,review,ai-runs}-1440x900-authenticated.png` | Authenticated workspace routes | 1440x900 | Desktop management coverage |
| `artifacts/authenticated/manage{-dashboard,-questions,-mistakes,-review}-390x844-authenticated.png` | Authenticated legacy manager/workspace routes | 390x844 | Mobile management coverage; legacy manager table clipping visible |
| `artifacts/clean-instance/{home,blog,notes,mistakes,guestbook}-{1440x900-desktop,390x844-mobile}.png` | Fresh-server public smoke set | 1440x900, 390x844 | Healthy asset-rendering confirmation |

Representative problem screenshots:

- `artifacts/mobile/mistakes-390x844-first.png`: UIR-001/003, raw oversized SVG/navigation.
- `artifacts/desktop/guestbook-1440x900-first.png`: UIR-001/005, missing layout plus perpetual loading content.
- `artifacts/mobile/guestbook-390x844-first.png`: UIR-005, form surface cannot provide meaningful feedback.
- `artifacts/mobile/wuthering-waves-390x844-first.png`: UIR-006, mobile technical-content hierarchy target after stylesheet recovery.
- `artifacts/authenticated/manage-390x844-authenticated.png`: UIR-007, legacy management table truncates metadata and hides actions on mobile.
