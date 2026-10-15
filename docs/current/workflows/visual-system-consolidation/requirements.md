# Requirements

## Functional Requirements

### VS-REQ-01 Visual foundation

- Inventory runtime theme variables, repeated surface styles, spacing, radius, shadow, border, typography, focus, motion, and layer usage.
- Define a minimal shared token proposal from current usage evidence.
- Preserve the existing teal brand identity while separating public editorial surfaces from dense administrator surfaces.
- Treat supplied screenshots as design references, not pixel-perfect production targets.

### VS-REQ-02 Public navigation

- Define one public desktop top navigation with floating, sticky, transparent, compact, and menu-open states.
- Define desktop dropdown navigation for grouped public destinations.
- Define mobile sticky topbar, hamburger trigger, and drawer navigation.
- Do not leave the new top navigation active alongside the legacy public `VerticalNav` or mobile bottom navigation after cutover.
- Preserve public access to notes, blogs, mistakes, and public detail pages.

### VS-REQ-03 Administrator navigation

- Define a grouped sidebar with `232px` expanded and `64px` collapsed target widths.
- Collapse must be user-triggered, not hover-triggered, and must preserve a visible active state and accessible tooltips.
- Define mobile administrator navigation through a focus-contained drawer.
- Persist sidebar preference only as display state; it must not affect authorization or route availability.

### VS-REQ-04 Breadcrumbs and anchors

- Breadcrumbs appear on meaningful detail, edit, and nested management pages, not mechanically on every list page.
- Desktop breadcrumbs show at most three meaningful levels; mobile shows a back destination and current label.
- Long-form blog and note details expose H2/H3 anchor navigation with one stable active section.
- Anchor scrolling must account for the sticky topbar, update the hash without noisy history entries, and provide a mobile bottom-sheet directory.

### VS-REQ-05 Overlay primitives

- Modal, Drawer, and Popover must have distinct responsibility boundaries.
- Shared overlays must define portal ownership, role, label, Escape handling, outside interaction, scroll lock, background isolation, focus entry, focus containment where required, and focus restoration.
- Long settings, filters, supporting detail, and AI assistance use Drawer rather than an oversized Modal.
- Short confirmation and short forms use Modal; anchored quick choices use Popover.
- Avoid simultaneous overlays except an explicitly supported confirmation Modal opened from a Drawer.

### VS-REQ-06 Context actions

- Desktop object-scoped commands support pointer right-click, `Shift+F10`, and the keyboard Menu key.
- Every context action remains available through a visible or focus-revealed more-actions button.
- Mobile uses an Action Sheet driven by the same action definition; long press may be supplementary but not required.
- Public text, input, link, code, and blank-page native context behavior remains intact.
- Multi-selection behavior, disabled actions, dangerous actions, and permission visibility are explicit.
- Destructive actions require a confirmation Modal and backend authorization.

### VS-REQ-07 Loading and empty states

- Navigation dimensions remain stable while authentication or content state resolves.
- Navigation itself does not use a skeleton that causes layout shift.
- Content loading uses representative skeletons; empty states provide one relevant next action without decorative card nesting.

## Non-Functional Requirements

- Accessibility: preserve accessible names, meaningful image alt text, browser zoom, keyboard operation, visible focus, semantic roles, background isolation, and focus restoration.
- Responsive behavior: verify desktop, tablet, and mobile layouts without overlapping navigation, drawers, content, or browser safe areas.
- Performance: quantify bundle and render impact before broad replacement; scroll state must not trigger high-frequency layout work.
- Security: frontend visibility never replaces backend authorization; anonymous visitors must not see protected actions during session loading.
- Compatibility: no route removal, dependency addition, Tailwind rewrite, or site-wide CSS migration without a separately approved implementation task.
- Auditability: each migrated consumer must have source, test, browser, and rollback evidence.

## Exclusions

- No marketing landing-page redesign.
- No full-site beige editorial recolor.
- No new state library or broad UI framework.
- No change to backend contracts, authentication semantics, or content persistence.
- No implementation before explicit approval of [tasks.md](./tasks.md).
