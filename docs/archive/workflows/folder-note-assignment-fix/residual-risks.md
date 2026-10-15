# Residual Risks

## RISK-001

Risk type: validation

Risk description: Full authenticated browser verification of selecting a real folder, moving content, and creating a new note inside that folder was not completed because the in-app Browser plugin blocked `http://localhost:2025/notes`.

Impact scope: final UI confidence for the authenticated notes workspace flow.

Severity: medium

Current status: partially mitigated

Mitigation evidence:

- Backend schema/router checks passed.
- Folder listing count regression check passed.
- Python compile check passed.
- `npx tsc --noEmit` passed.
- `npm run build` passed.
- Local HTTP checks confirmed `/notes` and `/write-note?folder_id=...` return 200/HTML from the running dev server.

Suggested action: complete authenticated browser verification in a browser surface that can access the local site.

Enter next-round requirements: no, unless the user wants browser-only acceptance evidence before merging.
