# Navigation, Overlay, and Context Action Specification

## 1. Purpose

This document turns the 2026-08-04 UI discussion into an implementation-ready interaction specification for navigation, shared overlays, and object-scoped context actions. It defines behavior and boundaries without authorizing implementation.

## 2. Reference Direction

The supplied references contribute different parts of the system:

- `assets/admin-login-cool-grid-reference.png`: cool white administrator/login surface, faint grid, teal primary action, low-contrast boundaries;
- `assets/editorial-whitespace-reference.png`: generous whitespace and restrained page chrome;
- `assets/editorial-grid-reference.png`: alignment through an implicit grid;
- `assets/editorial-card-microinteraction-reference.png`: restrained card focus and micro-interaction;
- `assets/editorial-masonry-reference.png`: content-only masonry inspiration, explicitly excluded from navigation;
- `assets/editorial-liquid-glass-reference.png`: restrained translucent navigation and tool surfaces;
- `assets/editorial-skeleton-reference.png`: representative loading placeholders;
- `assets/editorial-empty-state-reference.png`: guided empty states;
- `assets/overlay-modal-drawer-popover-reference.png`: responsibility separation between Modal, Drawer, and Popover.

The project adopts the structural principles, not the screenshots' full beige palette or promotional composition.

## 3. Visual Language

### 3.1 Shared identity

- Teal remains the primary brand, active, focus, and primary-action color.
- Cool white, neutral gray, and charcoal support operational surfaces.
- A restrained warm white may support public reading surfaces.
- Brick red is a secondary editorial accent for category, quotation, or emphasis and is not a competing navigation active color.
- Translucency is limited to navigation and overlay surfaces where background continuity is useful.

### 3.2 Public and administrator surfaces

Public reading surfaces prioritize whitespace, typography, grid alignment, and content hierarchy. Administrator surfaces prioritize scanning, stable controls, clear grouping, and compact repetition. Shared controls keep the same icon language, focus treatment, and motion timing.

## 4. Navigation System

### 4.1 Public desktop top navigation

The public desktop navigation has three states:

| State | Geometry | Surface |
| --- | --- | --- |
| Top | approximately `72px` high, `16px` from viewport top, `1120-1200px` content axis | transparent or lightly translucent |
| Scrolled | approximately `56px` high, sticky at `top: 0` | cool white at about 92% opacity, blur, border, subtle shadow |
| Menu open | stable compact geometry | forced solid-enough surface for menu contrast |

The transition begins after approximately `48px` of scroll and uses hysteresis to prevent flicker around the threshold. Font size does not scale; padding, background, border, shadow, and position change over `180-220ms`. Reduced-motion users receive an immediate state change.

Recommended grouping:

```text
Home
Content
  Blog
  Notes
  Mistakes
Explore
  Discover
  Guestbook
  About
```

The parent destination remains active when a child route is active. The top navigation replaces the existing public desktop vertical navigation after a separately validated cutover.

### 4.2 Desktop dropdown

- Open after about `120ms` hover intent and close after about `180ms` exit tolerance.
- Also open by click and keyboard focus.
- Support Tab, arrow navigation where implemented, Enter, Escape, outside click, and focus restoration.
- Use one `200-240px` menu surface with icon, label, and optional concise supporting text.
- Do not introduce third-level navigation.
- The menu is a single surface; menu items do not become nested decorative cards.

### 4.3 Administrator sidebar

- Expanded target width: `232px`.
- Collapsed target width: `64px`.
- Collapse is controlled by a button, not pointer hover.
- Group labels disappear when collapsed; icons remain stable and expose accessible tooltips.
- Active routes retain a teal-tinted background and an additional non-color indicator.
- The preference may persist locally as presentation state.
- The sidebar remains sticky within the administrator shell and never authorizes routes.

### 4.4 Mobile topbar and navigation drawer

- Sticky topbar target height: `56px` plus safe-area handling.
- Hamburger trigger on the left; current destination or brand in the stable center region; one high-priority utility on the right.
- The left drawer target is `min(320px, 86vw)`.
- Drawer navigation is grouped into public content, exploration, and administrator destinations when authenticated.
- Opening locks body scroll, isolates background content, moves focus into the drawer, and supports Escape, close button, overlay click, and route-change close.
- After validated cutover, the new mobile topbar/drawer replaces the public bottom navigation to avoid two competing primary navigation systems.

### 4.5 Breadcrumbs

- Show on detail, edit, and nested management pages where hierarchy aids orientation.
- Do not show mechanically on every top-level list.
- Desktop uses at most three meaningful visible levels; the current item is not a link and long labels truncate.
- Mobile shows a back destination and current label rather than a long trail.
- Breadcrumbs sit above the page title and align with the content grid, not inside the primary navigation.

### 4.6 Anchor navigation

- Long blog and note details expose H2 and H3 destinations.
- Desktop uses a right-side sticky directory with offset for the compact topbar.
- Mobile uses a directory button that opens a bottom Drawer.
- Scroll observation resolves one stable active section using a topbar-aware root margin.
- Clicking an anchor uses smooth scrolling unless reduced motion is requested.
- Hash updates use replacement semantics so scrolling does not flood browser history.

## 5. Overlay System

### 5.1 Decision table

| Need | Primitive |
| --- | --- |
| Confirmation, short form, blocking decision, immersive preview | Modal |
| Navigation, long configuration, filter, supporting detail, AI assistance | Drawer |
| Anchored dropdown, account menu, sort, quick choice | Popover |
| Desktop object-scoped command selection | Context Menu |
| Mobile object-scoped command selection | Action Sheet |

### 5.2 Modal

- Desktop width presets: approximately `440px`, `560px`, and `720px`; immersive viewers may use an explicit viewport-sized variant.
- Short confirmations may remain centered on mobile; longer forms become a bottom or full-height Drawer.
- Structure is title, optional description, content, and action footer.
- Primary action is visually clear; dangerous actions are red and require explicit confirmation language.
- Forms with unsaved work do not close on overlay click by default.
- Modal content does not contain decorative cards merely to create hierarchy.

### 5.3 Drawer

- Left: navigation.
- Right: settings, filters, supporting detail, diagnostics, and AI tools.
- Bottom: mobile directory, quick filters, and Action Sheet behavior.
- Desktop content drawers target `420-480px`.
- Long drawers use a fixed header, scrollable body, and fixed footer when actions are present.
- Existing long home configuration is a candidate for right-Drawer migration.

### 5.4 Popover

- Target width: `200-320px`.
- Anchored to its trigger and automatically repositioned away from viewport edges.
- Closes on selection, Escape, or outside interaction.
- Desktop may use hover intent for navigation dropdowns; mobile always requires explicit activation.
- Popover does not contain long scrolling forms or dangerous confirmations.

### 5.5 Shared accessibility and layering

Every shared overlay defines portal ownership, semantic role, accessible name, initial focus, keyboard containment where modal behavior requires it, background isolation, scroll locking, Escape behavior, outside-click behavior, and focus restoration.

Recommended layer scale:

```text
Sticky navigation       40
Popover / Dropdown      60
Drawer                  70
Modal                   80
Toast                  100
```

Two overlays do not stack except an explicitly supported confirmation Modal opened from a Drawer.

## 6. Context Actions and Right-Click

### 6.1 Ownership boundary

Custom right-click is enabled only on clear business objects:

- note, blog, and mistake cards;
- administrator table rows;
- folder, tag, subject, and knowledge-point nodes;
- image and attachment records;
- structured editor blocks when a block owns meaningful commands.

Native browser behavior remains on body text, code, links, input fields, text areas, general images, and page whitespace unless a separately documented product need overrides it.

### 6.2 Action structure

Recommended order:

```text
Open
Open in new tab
----------------
Edit
Copy link
Duplicate
----------------
Move to...
Change status
----------------
Delete
```

The target menu width is `220-240px`; target rows are `36-40px` high with stable `16px` icons. Dangerous actions are isolated, labeled, and colored red.

### 6.3 Follow-up routing

| Context action | Result |
| --- | --- |
| Open, copy link, simple visibility toggle | execute immediately |
| Simple status or classification choice | Popover or compact choice menu |
| Move, bulk organization, supporting detail | Drawer |
| Rename or short field edit | Modal |
| Delete, overwrite, discard unsaved content | confirmation Modal |
| Mobile context action | Action Sheet |

Complex actions close the Context Menu before opening the next overlay. Deep nested context submenus are avoided.

### 6.4 Pointer and keyboard behavior

- Pointer right-click opens near the pointer and flips or clamps away from viewport edges.
- `Shift+F10` and the keyboard Menu key open the same actions at the focused object's anchor.
- Arrow keys move through actions; Home and End move to boundaries; Enter activates; Escape closes.
- Closing restores focus to the original object.
- A visible or focus-revealed more-actions button exposes the same actions, so right-click is never the only entry.

### 6.5 Mobile behavior

Mobile uses the visible more-actions button to open a bottom Action Sheet. Long press may be an optional accelerator but is never the required path because it conflicts with operating-system and browser gestures.

### 6.6 Multi-selection

- Right-clicking an object already in the selection applies eligible actions to the selection.
- Right-clicking an object outside the selection replaces the selection with that object.
- The menu communicates the selected count when multiple objects are targeted.
- Unsupported bulk actions are disabled with an understandable reason.
- Bulk destructive confirmation states item count and object type.

### 6.7 Permission behavior

- Anonymous visitors retain native browser behavior and never receive administrator actions.
- Administrator actions appear only after session state is resolved.
- Frontend visibility is presentation only; backend authorization validates every protected action.
- Session expiry closes the menu, prevents optimistic protected success, and reports a concise error.

### 6.8 Shared action model

Desktop Context Menu and mobile Action Sheet use one domain-neutral action description, conceptually:

```ts
type ContextAction = {
  id: string
  label: string
  icon: LucideIcon
  group: 'open' | 'edit' | 'organize' | 'danger'
  disabled?: boolean
  variant?: 'default' | 'danger'
  run: () => void
}
```

Domain services still own mutations. The shared UI model does not move API requests into presentation components.

## 7. Loading and Empty States

- Authentication-dependent navigation reserves stable geometry until state resolves; protected controls do not flash for anonymous users.
- Navigation does not show layout-shifting skeletons.
- Content lists use representative skeleton structures rather than blank surfaces.
- Empty states contain a concise title, one helpful explanation, and one relevant next action where the user can act.

## 8. Recommended Pilot and Migration Order

1. Audit and harden overlay primitives without migrating consumers.
2. Pilot shared context actions in notes list, knowledge sidebar, and administrator content list.
3. Validate pointer, keyboard, mobile Action Sheet, multi-select, permission, and destructive confirmation behavior.
4. Introduce administrator sidebar collapse and breadcrumb rules.
5. Introduce public top navigation and dropdown behind a controlled cutover from `VerticalNav`.
6. Introduce public mobile topbar/drawer behind a controlled cutover from bottom navigation.
7. Improve article anchor navigation and mobile directory.
8. Migrate remaining page-specific overlays incrementally.

## 9. Validation Contract

- Component tests: state transitions, positioning, dismissal, focus, roles, keyboard commands, disabled and danger behavior.
- Permission tests: anonymous, administrator, loading, logout, and expired-session states.
- Browser checks: desktop and mobile navigation, scroll transitions, dropdown hover/focus, drawer isolation, Modal focus, anchor highlighting, right-click edge positioning, and Action Sheet parity.
- Responsive checks: no overlap with topbars, safe areas, content, or other overlays.
- Reduced-motion checks: no required information depends on animation.
- Engineering checks: `npx tsc --noEmit`, targeted tests, build-sensitive validation, and bundle comparison.

## 10. Explicit Non-Goals

- No universal override of browser context menus.
- No simultaneous public top navigation and legacy vertical/bottom navigation after cutover.
- No full-site editorial recolor.
- No broad dependency or UI-framework addition.
- No frontend-only permission boundary.
- No automatic execution from this specification.
