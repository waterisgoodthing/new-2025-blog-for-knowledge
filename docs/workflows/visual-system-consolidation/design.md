# Design

## 1. Current-State Basis

Current source already exposes runtime theme variables from `src/app/layout.tsx` and repeatedly builds translucent surfaces with component-local utility classes. The historical glassmorphism proposal is not an implementation contract because its dedicated stylesheet and Tailwind extension are absent.

Navigation and overlays are also fragmented:

- public desktop routes use a hover-expanding `VerticalNav`;
- public mobile routes use a bottom navigation plus a bottom sheet for additional destinations;
- the administrator workspace has a grouped sidebar and a separate mobile drawer;
- article contents use a local `IntersectionObserver` implementation;
- Modal, Drawer, Context Menu, and page-specific dialog implementations do not yet share a complete accessibility and layering contract.

## 2. Product Direction

The design language is deliberately split by product responsibility while preserving common geometry and interaction rules:

- public reading surfaces: editorial whitespace, aligned grid, strong content hierarchy, restrained cards, and minimal visual chrome;
- administrator surfaces: cool white utility surfaces, faint teal structure, higher information density, and stable controls;
- shared navigation and overlays: restrained translucent treatment, clear borders, predictable focus, and the existing teal brand color for active states.

The warm editorial screenshots are references for whitespace, grid, hierarchy, micro-interaction, loading, and empty-state principles. They are not authorization to turn the full product into a beige, retro-editorial theme. Brick red may appear as a secondary editorial accent but must not compete with teal navigation and action states.

## 3. Navigation Architecture

Navigation modes are assigned by context rather than stacked on every page:

| Context | Primary navigation | Secondary navigation |
| --- | --- | --- |
| Public desktop | floating top navigation that becomes sticky and solid on scroll | dropdowns, breadcrumbs, article anchors |
| Administrator desktop | click-collapsible grouped sidebar | topbar and breadcrumbs |
| Mobile | sticky topbar with hamburger-triggered drawer | compact breadcrumb and bottom-sheet article contents |

The public top navigation replaces the current public desktop `VerticalNav`; the proposed mobile topbar and drawer replace the current public bottom navigation. The implementation task must verify these product decisions before removing either legacy navigation.

## 4. Overlay Architecture

Overlay selection follows task size and interruption level:

| Primitive | Responsibility |
| --- | --- |
| Modal | confirmation, short forms, blocking decisions, immersive preview |
| Drawer | navigation, configuration, filters, supporting detail, AI assistance |
| Popover | anchored navigation dropdowns, account menus, sort and quick choices |
| Context Menu | desktop object-scoped command selection |
| Action Sheet | mobile rendering of the same object-scoped commands |

Context Menu selects an action; it does not host complex workflows. A selected action may execute immediately or open a Popover, Drawer, or Modal according to the shared specification.

## 5. Shared Interaction Principles

- Right-click is an efficiency enhancement, never the only way to reach an action.
- Text, input, link, code, image-download, and blank-page browser behavior is preserved unless a product-specific object clearly owns the event.
- Administrator controls appear only after session state is known; backend authorization remains the security boundary.
- Floating, sticky, drawer, dropdown, and context states use stable dimensions so content does not shift while state changes.
- Motion is limited to meaningful position, opacity, surface, and spacing transitions and respects `prefers-reduced-motion`.
- Nested decorative cards and stacked translucent surfaces are avoided.

## 6. Detailed Specification

Exact dimensions, route assignments, menu structures, responsive behavior, overlay routing, context actions, focus behavior, and migration recommendations are defined in [navigation-overlay-context-actions.md](./navigation-overlay-context-actions.md).

## 7. Rollback

Implementation must be incremental. Each new shared primitive retains the existing consumer until route-level browser validation succeeds. Rollback restores the previous consumer without changing routes, backend contracts, or public access rules.
