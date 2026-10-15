# Design

## Test Warning Fix

Run the complete Vitest suite with full stderr output, use the warning stack and
focused test runs to identify each asynchronous state update, then apply the
smallest test-only synchronization change. Prefer Testing Library `waitFor` for
observable UI completion and `act` only when directly advancing an update source.
Do not change component behavior or the test framework.

## Manage Avatar LCP

Keep the existing `next/image` component, source, dimensions, styles, and
anonymous/authenticated branching. Add `loading="eager"` and
`fetchPriority="high"` only to the anonymous `/manage` avatar identified by the
existing LCP warning.

## Validation

Validate in increasing scope: focused warning-producing tests, complete frontend
suite, TypeScript, production build, then `/manage` at 1280x800, 1440x900, and
390x844. Browser validation checks console guidance, image rendering, layout,
and loading attributes without authenticating or changing data.
