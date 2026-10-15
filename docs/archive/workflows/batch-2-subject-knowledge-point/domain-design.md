# Domain Design

## Domain Summary

Batch 2 establishes the knowledge organization foundation:

```text
Subject
  -> Knowledge Point Tree
      -> future Question / Mistake / Review references
```

Subject and Knowledge Point belong to the private learning management side. They are not public content objects and do not replace Blog, Note, Question, Mistake, or Review domains.

## Subject Domain

### Definition

Subject is the top-level private learning namespace used to organize a coherent body of study.

The product-facing label may be "Subject", but the domain meaning is broader than a school subject. A Subject may represent:

- a discipline: `数学`
- a course: `高等数学`
- an exam subject: `考研数学`
- a self-study track: `算法`

### Decision

Subject represents a **learning track / knowledge namespace**, not only a discipline, course, or exam subject.

### Rationale

- The personal learning system needs one stable top-level organizer before future Question, Mistake, and Review objects exist.
- Splitting discipline/course/exam into separate tables would be premature for MVP and would force Batch 2 to design scheduling, curriculum, and exam-planning concerns.
- A single Subject can still express the user's real use cases through naming and optional metadata later.
- The Knowledge Point tree can carry deeper structure, so Subject should remain a coarse namespace.

### Boundary

Subject owns:

- name and optional description
- status
- sorting among Subjects
- root namespace for Knowledge Points

Subject does not own:

- question content
- mistake analysis
- review schedule
- mastery score
- AI suggestions
- attachments
- public publication state
- analytics aggregates

### Lifecycle

Subject lifecycle:

```text
active -> archived
```

Meanings:

- `active`: appears in normal management selectors and tree views.
- `archived`: retained for history and references, hidden from default creation selectors unless explicitly included.

Hard delete is not the default lifecycle. If future implementation allows delete, it must reject delete while Knowledge Points or future business objects reference the Subject.

### Status

Recommended status enum:

```text
active
archived
```

No `draft` status is needed in Batch 2. Subject creation is a simple administrator action, not an AI/generated or high-risk review object.

### Relationship To Knowledge Point

One Subject has many Knowledge Points.

Each Knowledge Point belongs to exactly one Subject. Subject is the partition key for the tree.

## Knowledge Point Domain

### Definition

Knowledge Point is a named concept, topic, method, formula, section, or unit of understanding inside one Subject.

Examples:

- `高等数学`
- `函数`
- `三角函数`
- `极限`
- `线性代数`

### Tree Model

Knowledge Point uses an adjacency-list tree:

```text
knowledge_points.id
knowledge_points.parent_id -> knowledge_points.id
```

Rules:

- `parent_id = null` means root node under the Subject.
- A child must have the same `subject_id` as its parent.
- A node cannot be its own parent.
- A node cannot be moved under its descendant.
- Sibling order is controlled by `sort_order`, then stable `id`.

### Unlimited Hierarchy

The domain allows unlimited depth.

Implementation guidance:

- The database should not hard-code a depth limit.
- UI may progressively render depth for usability.
- API may return full tree for small personal data, but should support scoped subtree queries for future scale.

### Future Mind-Map Readiness

The tree design supports mind-map rendering because every node has:

- stable ID
- display name
- optional parent
- sort order
- status
- description for detail panels

Mind-map layout, graph edges, cross-links, and visualization components are not part of Batch 2.

### Detail Page Support

Each Knowledge Point needs a detail page in the management workspace.

Detail page responsibilities are design-only in this batch:

- show identity fields
- show parent path
- show children summary
- show future reference slots for Questions, Mistakes, and Review without implementing them

### Relationship To Future Domains

Future Question, Mistake, and Review may reference Knowledge Points by ID, but Batch 2 does not design their fields, APIs, or UI.

Allowed statement:

```text
Future domains may use knowledge_point_id or a link table to associate with Knowledge Points.
```

Forbidden in Batch 2:

```text
Designing question schema, mistake schema, review schedule, attachment upload, AI suggestions, or analytics.
```

## Invariants

- Subject name must be non-empty after trimming.
- Knowledge Point name must be non-empty after trimming.
- Subject names should be unique in the single-admin workspace.
- Knowledge Point sibling names should be unique under the same parent within a Subject.
- Parent and child must share Subject.
- Archived Subject should hide its tree from default selectors, but not delete nodes.
- Archiving a Knowledge Point archives its full subtree recursively.
- Archived Knowledge Point remains referenceable by old records.

## Archive Strategy

Knowledge Point archive uses subtree archive.

Example:

```text
数学
└── 高等数学
    └── 函数
        └── 三角函数
```

After:

```text
archive(函数)
```

Result:

```text
数学
└── 高等数学
    └── 函数 archived
        └── 三角函数 archived
```

Rationale:

- Parent and child have strong semantic dependency.
- Active children under archived parents create orphan-like default query behavior.
- Mind-map rendering should not show broken active branches under hidden parents.
- Service logic must recursively update descendants.

## Examples

```text
Subject: 数学

Knowledge Points:
- 高等数学
  - 函数
    - 三角函数
  - 极限
- 线性代数
```

This is represented as:

```text
数学 = subjects row
高等数学 = knowledge_points row, subject_id=数学, parent_id=null
函数 = knowledge_points row, subject_id=数学, parent_id=高等数学
三角函数 = knowledge_points row, subject_id=数学, parent_id=函数
极限 = knowledge_points row, subject_id=数学, parent_id=高等数学
线性代数 = knowledge_points row, subject_id=数学, parent_id=null
```
