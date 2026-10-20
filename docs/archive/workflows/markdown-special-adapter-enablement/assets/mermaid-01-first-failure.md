# Mermaid-01 first structural failure

Date: 2026-08-16

Command:

```text
env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx vitest run src/lib/markdown-poc/__tests__/mermaid-isolated.test.ts --reporter=verbose
```

Initial result: `1 file failed / 2 tests failed`.

- The valid synthetic flowchart produced no `svg[data-poc-mermaid]`; the current PoC still returned inert code.
- The hostile Mermaid fixture produced `outcome: inert` instead of the required exact local fallback with `LOCAL_FALLBACK`.

This is the retained pre-implementation proof. The final focused result after the isolated flowchart placeholder, source gate, and SVG sanitizer was `1 file / 3 tests passed`. It does not by itself prove browser rendering or G2.
