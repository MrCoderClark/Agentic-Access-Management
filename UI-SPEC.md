# AgentGuard — UI Design Specification

## Design Philosophy

AgentGuard's interface should feel like a **mission control center for identity governance** — authoritative, precise, and calm under pressure. Not a generic SaaS dashboard. Not a hacker terminal. A tool that security engineers trust and employees actually want to use.

**Three principles:**

1. **Command, not decoration** — Every pixel earns its place. No gradient hero sections, no floating shapes, no "AI sparkle" animations. Information density is a feature.
2. **Warm authority** — Deep ink backgrounds with amber accents signal premium confidence, not cold corporate blue. The palette says "we've got this handled."
3. **Transparent machines** — Agent decisions are shown as traceable reasoning chains, not black boxes. The UI makes AI legible.

---

## Color System

### Why Not the Default

Most AI/security dashboards default to slate-900 + electric blue or neon green. AgentGuard uses **deep indigo-ink + amber** — a palette that reads as institutional authority (think: diplomatic seals, control rooms) rather than startup SaaS.

### Dark Theme (Primary)

```css
:root {
  /* Surfaces — warm-tinted darks, NOT pure black or generic slate */
  --bg-root:        #0C0E14;    /* Deep ink, slight blue warmth */
  --bg-surface:     #12151E;    /* Card/panel background */
  --bg-elevated:    #1A1D2B;    /* Modals, dropdowns, hover states */
  --bg-subtle:      #222639;    /* Selected rows, active nav items */

  /* Text */
  --text-primary:   #E8E6E1;    /* Warm white — not pure #FFF */
  --text-secondary: #8B8D98;    /* Muted labels, timestamps */
  --text-tertiary:  #565869;    /* Disabled, placeholder */

  /* Accent — Amber/Gold (the signature) */
  --accent:         #D4930D;    /* Primary CTA, active states, key indicators */
  --accent-hover:   #E8A817;    /* Hover state */
  --accent-muted:   #D4930D1A;  /* 10% amber — subtle highlights, badge backgrounds */
  --accent-text:    #0C0E14;    /* Text on amber backgrounds */

  /* Semantic */
  --status-active:  #34D399;    /* Access granted, healthy, online */
  --status-warning: #FBBF24;    /* Pending, medium risk, expiring soon */
  --status-danger:  #EF4444;    /* Denied, critical risk, revoked, errors */
  --status-info:    #60A5FA;    /* Informational, links, metadata */

  /* Borders & Dividers */
  --border:         #1F2233;    /* Default borders — barely visible */
  --border-strong:  #2E3148;    /* Emphasized borders, input focus */
  --ring:           #D4930D66;  /* Focus ring — amber at 40% */

  /* Agent-specific */
  --agent-pulse:    #D4930D;    /* Live agent activity indicator */
  --agent-reasoning:#60A5FA;    /* RAG citation links, reasoning highlights */
  --confidence-high:#34D399;    /* Confidence > 0.8 */
  --confidence-mid: #FBBF24;    /* Confidence 0.5–0.8 */
  --confidence-low: #EF4444;    /* Confidence < 0.5 */
}
```

### Light Theme (Employee Portal)

The employee self-service portal defaults to light mode — most employees aren't staring at dashboards all day.

```css
:root[data-theme="light"] {
  --bg-root:        #F6F5F2;    /* Warm off-white, not clinical #FFF */
  --bg-surface:     #FFFFFF;
  --bg-elevated:    #FFFFFF;
  --bg-subtle:      #EDECEA;

  --text-primary:   #1A1B1E;
  --text-secondary: #6B6D7B;
  --text-tertiary:  #9B9DA8;

  --accent:         #B37A00;    /* Slightly darker amber for light bg contrast */
  --accent-hover:   #996800;
  --accent-muted:   #B37A000F;

  --border:         #E5E4E1;
  --border-strong:  #D4D3CF;
}
```

### Color Usage Rules

| Element | Color | Never |
|---------|-------|-------|
| Primary CTA buttons | `--accent` on `--bg-surface` | Blue CTAs (too generic) |
| Navigation active state | `--accent-muted` background + `--accent` text/icon | Bold backgrounds on nav items |
| Status badges | Semantic colors with matching 10%-opacity backgrounds | Color-only — always pair with icon or text label |
| Links in body text | `--status-info` | Underlined amber (clashes with CTA) |
| Risk score numbers | Color-coded (green/amber/red) with the numeric value visible | Color-only indicators |
| Data table row hover | `--bg-elevated` | Amber highlight on rows (too aggressive) |
| Agent decision cards | `--bg-surface` with `--border` left accent strip | Glowing borders, pulsing backgrounds |

---

## Typography

### Font Selection

**Headings + Body:** [Geist](https://vercel.com/font) (by Vercel)
- Clean, slightly condensed, designed for interfaces
- Distinguishes AgentGuard from the Inter/Plus Jakarta crowd
- Excellent weight range (100–900)
- Falls back to system sans-serif

**Data + Code + Agent Logs:** [Geist Mono](https://vercel.com/font)
- Matched to Geist for visual cohesion
- Used for: risk scores, timestamps, agent reasoning chains, RAG citations, policy conditions, access grant IDs

**Fallback alternative** (if Geist licensing is a concern): **IBM Plex Sans** + **IBM Plex Mono** — similar personality, fully open source.

### Type Scale

```css
/* Using a 1.2 minor third scale, base 16px */
--text-xs:    0.75rem;   /* 12px — timestamps, fine metadata */
--text-sm:    0.875rem;  /* 14px — secondary labels, table cells */
--text-base:  1rem;      /* 16px — body text, input values */
--text-lg:    1.125rem;  /* 18px — card titles, section labels */
--text-xl:    1.25rem;   /* 20px — page section headings */
--text-2xl:   1.5rem;    /* 24px — page titles */
--text-3xl:   2rem;      /* 32px — dashboard KPI numbers */
--text-4xl:   2.5rem;    /* 40px — hero stat on overview page */
```

### Type Rules

| Context | Font | Weight | Size | Tracking |
|---------|------|--------|------|----------|
| Page title | Geist | 600 | text-2xl | -0.025em |
| Section heading | Geist | 600 | text-xl | -0.02em |
| Card title | Geist | 500 | text-lg | -0.01em |
| Body text | Geist | 400 | text-base | normal |
| Table header | Geist | 500 | text-sm | 0.02em (uppercase) |
| Table cell | Geist | 400 | text-sm | normal |
| KPI number | Geist Mono | 600 | text-3xl | -0.03em |
| Risk score | Geist Mono | 700 | text-lg | normal |
| Timestamp | Geist Mono | 400 | text-xs | normal |
| Agent reasoning | Geist Mono | 400 | text-sm | normal |
| Code/policy conditions | Geist Mono | 400 | text-sm | normal |
| Button label | Geist | 500 | text-sm | 0.01em |

---

## Layout Architecture

### Shell Structure

AgentGuard uses a **compact sidebar + contextual top bar** — not the chunky 280px sidebar that every shadcn template ships with.

```
┌──────────────────────────────────────────────────────────────────┐
│ ┌──┐ ┌───────────────────────────────────────────────────────┐   │
│ │  │ │ [Breadcrumb / Context]          [Search] [Notif] [Avi]│   │
│ │  │ ├───────────────────────────────────────────────────────┤   │
│ │  │ │                                                       │   │
│ │  │ │                                                       │   │
│ │  │ │               MAIN CONTENT AREA                       │   │
│ │64│ │                                                       │   │
│ │px│ │            (scrolls independently)                    │   │
│ │  │ │                                                       │   │
│ │  │ │                                                       │   │
│ │  │ │                                                       │   │
│ │  │ │                                                       │   │
│ │  │ │                                                       │   │
│ └──┘ └───────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
  Sidebar                         Content
  (icon-only,                     (max-width: 1440px, centered)
   expands on hover
   to 220px with labels)
```

### Sidebar

- **Width**: 64px collapsed (icons only), 220px expanded on hover
- **Behavior**: Icon-only by default, expands on hover with smooth slide (200ms ease-out). Labels appear with a slight 50ms delay (stagger fade-in).
- **Background**: `--bg-root` (blends with page, no visible sidebar box)
- **Active indicator**: 3px left border in `--accent`, icon + label tinted `--accent`
- **Sections**: Dividers are 1px `--border` lines with 12px vertical margin, no section labels

**Navigation items (top to bottom):**
```
[Logo mark]            ← AgentGuard logomark (shield + circuit motif, 32x32)
─────────
[Dashboard]            ← Overview / KPIs
[Requests]             ← Access request management
[Policies]             ← Policy editor
[Systems]              ← Connected systems
[Knowledge]            ← RAG document management
─────────
[Reviews]              ← Access review queue
[Agents]               ← Agent observatory
[Audit]                ← Audit log viewer
[Analytics]            ← Reports & charts
─────────
[Settings]             ← (bottom-pinned)
```

### Top Bar

- **Height**: 56px
- **Left**: Breadcrumb trail (e.g., "Dashboard / Access Requests / REQ-2847")
- **Right**: Global search (⌘K), notification bell with count badge, user avatar + role dropdown
- **Background**: `--bg-root` — seamless with content, separated by a 1px `--border` bottom line
- **Search**: Opens a command palette (⌘K) overlay — search across requests, users, systems, policies, knowledge base

### Content Area

- **Max width**: 1440px, centered with `auto` margins
- **Padding**: 32px horizontal, 24px vertical
- **Grid**: 12-column CSS grid, 24px gap
- **Sections within a page**: 32px vertical spacing between major sections, 16px between related cards

---

## Component Design Language

### Cards

Not the default shadcn rounded-lg + shadow. AgentGuard cards are **sharp, bordered, and structured**.

```css
.card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 8px;              /* Subtle rounding — not pill-shaped */
  padding: 20px;
  transition: border-color 200ms ease;
}
.card:hover {
  border-color: var(--border-strong);
}
```

**Card variants:**
- **Metric card**: KPI number (Geist Mono, text-3xl) + label below + sparkline inline
- **Status card**: Left border accent (3px) colored by status + icon + title + description
- **Decision card**: Agent avatar (small circle with agent color) + decision summary + expandable reasoning chain
- **Request card**: Requester avatar + system icon + status badge + risk score pill

### Buttons

```css
/* Primary — amber, used sparingly */
.btn-primary {
  background: var(--accent);
  color: var(--accent-text);
  font-weight: 500;
  font-size: var(--text-sm);
  letter-spacing: 0.01em;
  padding: 8px 16px;
  border-radius: 6px;
  transition: background 150ms ease;
}
.btn-primary:hover {
  background: var(--accent-hover);
}

/* Secondary — ghost with border */
.btn-secondary {
  background: transparent;
  color: var(--text-primary);
  border: 1px solid var(--border-strong);
  border-radius: 6px;
  padding: 8px 16px;
}
.btn-secondary:hover {
  background: var(--bg-elevated);
  border-color: var(--text-secondary);
}

/* Destructive — red, always requires confirmation */
.btn-destructive {
  background: var(--status-danger);
  color: #FFFFFF;
  border-radius: 6px;
  padding: 8px 16px;
}

/* Ghost — text-only, for inline actions */
.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
  padding: 6px 12px;
  border-radius: 6px;
}
.btn-ghost:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
}
```

**Button rules:**
- Only ONE primary (amber) button per screen section
- Approve/Deny buttons are always paired side-by-side, Deny is `btn-secondary` not `btn-destructive` (revoke is destructive, deny is not)
- Loading state: spinner replaces icon, label stays, button is disabled
- Icon + text buttons: icon left, 8px gap, icon is 16x16

### Status Badges

Distinctive treatment — **pill-shaped with tinted background + icon prefix**, not just colored text.

```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 9999px;
  font-size: var(--text-xs);
  font-weight: 500;
  font-family: 'Geist Mono', monospace;
}

/* Variants */
.badge-active    { background: #34D39915; color: #34D399; }
.badge-pending   { background: #FBBF2415; color: #FBBF24; }
.badge-denied    { background: #EF444415; color: #EF4444; }
.badge-expired   { background: #565869; color: var(--text-secondary); }
.badge-info      { background: #60A5FA15; color: #60A5FA; }
```

Each badge has a small Lucide icon prefix:
- Active: `check-circle` (12px)
- Pending: `clock` (12px)
- Denied: `x-circle` (12px)
- Expired: `timer-off` (12px)

### Risk Score Display

Risk scores are a core UI element. They need to be scannable at a glance.

```
┌─────────────────────┐
│  Risk: 0.23         │  ← Low risk: green text, green left accent
│  ████░░░░░░  LOW    │  ← Thin progress bar (4px height) + text label
└─────────────────────┘

┌─────────────────────┐
│  Risk: 0.67         │  ← Medium risk: amber text, amber left accent
│  ██████░░░░  MED    │
└─────────────────────┘

┌─────────────────────┐
│  Risk: 0.91         │  ← High risk: red text, red left accent
│  █████████░  HIGH   │  ← Bar pulses subtly at high risk (animation)
└─────────────────────┘
```

- Score displayed in Geist Mono, weight 700
- Always accompanied by a text label (LOW / MED / HIGH / CRITICAL)
- Never color-only — the bar + number + label triple ensures accessibility

### Data Tables

Tables are the workhorse UI. They need to handle hundreds of rows without looking cluttered.

```css
.table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
}
.table th {
  font-family: 'Geist', sans-serif;
  font-weight: 500;
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-strong);
  position: sticky;
  top: 0;
  background: var(--bg-root);
}
.table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  color: var(--text-primary);
  vertical-align: middle;
}
.table tr:hover td {
  background: var(--bg-elevated);
}
```

**Table conventions:**
- Row height: 48px minimum (touch-friendly)
- Status columns use badge components, not colored text
- Timestamp columns use Geist Mono, relative time ("2h ago") with absolute on hover tooltip
- Sortable columns show a chevron-up/down icon (Lucide `chevrons-up-down`, 14px)
- First column often has a checkbox for bulk actions
- Clickable rows: entire row is clickable, cursor-pointer, navigates to detail view

### Forms & Inputs

```css
.input {
  background: var(--bg-root);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 12px;
  font-size: var(--text-sm);
  color: var(--text-primary);
  transition: border-color 150ms ease;
  width: 100%;
}
.input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--ring);
}
.input::placeholder {
  color: var(--text-tertiary);
}

.label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 6px;
  display: block;
}
```

---

## Key Page Designs

### 1. Dashboard Overview

The landing page after login. Shows the org's access health at a glance.

```
┌──────────────────────────────────────────────────────────────┐
│  Access Overview                                    [Today ▾]│
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ OPEN     │ │ AUTO-    │ │ AVG      │ │ POSTURE  │       │
│  │ REQUESTS │ │ APPROVED │ │ DECISION │ │ SCORE    │       │
│  │    12    │ │   73%    │ │   4.2s   │ │   87     │       │
│  │ +3 today │ │ ▲ +5%   │ │ ▼ -1.1s  │ │ ▲ +2    │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│                                                              │
│  ┌────────────────────────────┐ ┌────────────────────────┐  │
│  │ Recent Agent Decisions     │ │ Risk Distribution      │  │
│  │                            │ │                        │  │
│  │ ● Request Agent → APPROVED │ │ [stacked bar chart]    │  │
│  │   "GitHub org access for   │ │                        │  │
│  │    engineering onboard"    │ │ Low  ████████████ 67%  │  │
│  │   Risk: 0.12  Conf: 0.94  │ │ Med  █████░░░░░░ 22%  │  │
│  │   2 min ago                │ │ High ██░░░░░░░░░ 11%  │  │
│  │                            │ │                        │  │
│  │ ● Policy Agent → ESCALATED│ │                        │  │
│  │   "AWS prod console - non-│ │                        │  │
│  │    standard request"      │ │                        │  │
│  │   Risk: 0.71  Conf: 0.58  │ │                        │  │
│  │   8 min ago                │ │                        │  │
│  │                            │ │                        │  │
│  │ [View all decisions →]     │ │                        │  │
│  └────────────────────────────┘ └────────────────────────┘  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Pending Approvals (3)                    [View all →] │  │
│  │                                                       │  │
│  │ [Avatar] Jane D. → Datadog (Read)  Risk 0.34  [✓][✗] │  │
│  │ [Avatar] Mike T. → AWS (Admin)     Risk 0.82  [✓][✗] │  │
│  │ [Avatar] Sara K. → GitHub (Write)  Risk 0.19  [✓][✗] │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

**Design notes:**
- KPI cards across the top: Geist Mono for the big number, Geist for label, sparkline trend arrow + delta
- "Recent Agent Decisions" list: each item has a colored dot (agent color), decision summary in plain language, risk + confidence in Geist Mono
- Pending approvals: inline approve/deny buttons, risk score pill, click row for detail
- All numbers use `tabular-nums` for column alignment

### 2. Agent Observatory

The most distinctive page — shows AI agent activity as a **live operations view**.

```
┌──────────────────────────────────────────────────────────────┐
│  Agent Observatory                         [Live ●] [Pause] │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ REQUEST  │ │ POLICY   │ │ PROVISION│ │ SENTINEL │       │
│  │ ● Active │ │ ● Active │ │ ○ Idle   │ │ ● Active │       │
│  │ 142 runs │ │ 138 runs │ │ 89 runs  │ │ 24/7     │       │
│  │ 0.91 avg │ │ 0.87 avg │ │ 99.2%    │ │ 3 alerts │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Decision Stream                        [Filter ▾]     │  │
│  │                                                       │  │
│  │  14:23:07  REQUEST   Parse: "I need Datadog access"  │  │
│  │            ─────────────────────────────────────────  │  │
│  │  14:23:07  RAG       Retrieved 4 docs (policy:2,     │  │
│  │                      precedent:1, system:1)           │  │
│  │            ─────────────────────────────────────────  │  │
│  │  14:23:08  POLICY    Risk: 0.23 | Confidence: 0.94   │  │
│  │                      Decision: AUTO_APPROVE           │  │
│  │                      Cited: access-policy-eng-v3.md   │  │
│  │            ─────────────────────────────────────────  │  │
│  │  14:23:08  PROVISION Okta: Added to datadog-readers   │  │
│  │                      Status: ✓ SUCCESS (1.2s)         │  │
│  │            ─────────────────────────────────────────  │  │
│  │  14:23:08  AUDIT     Event logged: access_granted     │  │
│  │                                                       │  │
│  │  ──── 14:22 ──────────────────────────────────────── │  │
│  │                                                       │  │
│  │  14:22:41  REQUEST   Parse: "Prod AWS console"       │  │
│  │  14:22:42  RAG       Retrieved 3 docs (policy:2,     │  │
│  │                      precedent:1)                     │  │
│  │  14:22:43  POLICY    Risk: 0.71 | Confidence: 0.58   │  │
│  │                      Decision: ESCALATE               │  │
│  │                      Reason: "Non-standard access     │  │
│  │                      pattern. No precedent for this   │  │
│  │                      role requesting prod console."   │  │
│  │                      Cited: prod-access-policy.md,    │  │
│  │                             least-privilege-sop.md    │  │
│  │                                                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌─────────────────────┐ ┌───────────────────────────────┐  │
│  │ Confidence Dist.    │ │ Agent Performance (7d)        │  │
│  │                     │ │                               │  │
│  │ [histogram]         │ │ [multi-line chart]            │  │
│  │                     │ │ — Decisions/hr                │  │
│  │ Mean: 0.84          │ │ — Avg confidence              │  │
│  │ P50:  0.89          │ │ — Escalation rate             │  │
│  │ <0.6: 8% (flagged)  │ │                               │  │
│  └─────────────────────┘ └───────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

**Design notes:**
- Agent status cards at top: pulsing green dot for active (CSS animation, 2s infinite, respects reduced-motion), hollow circle for idle
- Decision stream: styled as a **structured log** — timestamps in Geist Mono (text-xs, `--text-tertiary`), agent labels as colored chips, content in Geist Mono (text-sm)
- Each decision block is expandable — click to see full reasoning chain + RAG source documents
- RAG citations are clickable links (styled in `--agent-reasoning` blue) — open in a slide-over panel showing the source document chunk
- The stream auto-scrolls when "Live" is active, pauses when user scrolls up (like a terminal)
- Confidence distribution: small histogram using Recharts, green/amber/red bars
- Time separators in the stream: centered dashed line with timestamp label

### 3. Access Request Detail

When an admin clicks into a specific request — shows the full decision trail.

```
┌──────────────────────────────────────────────────────────────┐
│  ← Back to Requests                                         │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  REQ-2847                              [PENDING APPROVAL]││
│  │                                                         ││
│  │  Jane Doe → Datadog (Admin)                             ││
│  │  Engineering · Senior Engineer · Reports to: Mike T.    ││
│  │  Requested: Jun 7, 2026 14:23 UTC · Duration: 72h      ││
│  │  Justification: "Investigating prod latency spike,      ││
│  │  need admin access to create monitors and dashboards"   ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  Decision Trail                                              │
│  ─────────────────────────────────────────────────────────── │
│                                                              │
│  ┌─ PARSE ────────────────────────────────────────────────┐ │
│  │ System: Datadog    Permission: Admin    Duration: 72h  │ │
│  │ Requester context: Sr. Eng, 2yr tenure, 3 prior Datadog│ │
│  │ grants (all read-only), no policy violations           │ │
│  └────────────────────────────────────────────────────────┘ │
│      │                                                       │
│      ▼                                                       │
│  ┌─ RAG RETRIEVAL ────────────────────────────────────────┐ │
│  │ 4 documents retrieved:                                 │ │
│  │  📄 datadog-access-policy-v3.md         sim: 0.94     │ │
│  │  📄 admin-access-escalation-sop.md      sim: 0.87     │ │
│  │  📄 Past: REQ-2201 (similar, approved)  sim: 0.82     │ │
│  │  📄 datadog-system-doc.md               sim: 0.79     │ │
│  └────────────────────────────────────────────────────────┘ │
│      │                                                       │
│      ▼                                                       │
│  ┌─ POLICY EVALUATION ───────────────────────────────────┐  │
│  │ Risk Score: 0.61 (MEDIUM)   Confidence: 0.72          │  │
│  │                                                       │  │
│  │ Reasoning:                                            │  │
│  │ "Requester has history of read-only Datadog access    │  │
│  │ but has never held admin privileges. Policy           │  │
│  │ 'datadog-access-policy-v3' §3.2 requires manager     │  │
│  │ approval for admin tier. Similar request REQ-2201     │  │
│  │ was approved by manager after review. Recommending    │  │
│  │ approval with 72h TTL as requested."                  │  │
│  │                                                       │  │
│  │ Decision: NEEDS_APPROVAL                              │  │
│  │ Recommendation: APPROVE (with standard 72h TTL)       │  │
│  │ Approver: Mike T. (direct manager)                    │  │
│  └───────────────────────────────────────────────────────┘  │
│      │                                                       │
│      ▼                                                       │
│  ┌─ AWAITING APPROVAL ───────────────────────────────────┐  │
│  │ Sent to: Mike T. (Slack DM + email)                   │  │
│  │ Sent at: Jun 7, 2026 14:23 UTC                        │  │
│  │ SLA deadline: Jun 8, 2026 14:23 UTC (24h)             │  │
│  │                                                       │  │
│  │  ┌─────────────┐  ┌──────────────┐                    │  │
│  │  │  ✓ Approve  │  │  ✗ Deny      │                    │  │
│  │  └─────────────┘  └──────────────┘                    │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

**Design notes:**
- The decision trail is a **vertical connected flow** — each step is a bordered card with a label chip in the top-left corner
- Steps are connected by a thin vertical line (2px, `--border-strong`) with a small arrow
- RAG document references are clickable — slide-over panel shows the retrieved chunk
- Policy section references are highlighted (e.g., "§3.2") in `--accent` color
- The reasoning block uses Geist Mono at text-sm, with a subtle `--bg-elevated` background
- Approve button is `btn-primary` (amber), Deny is `btn-secondary` (ghost + border)

### 4. Employee Portal — Request Form

Clean, focused form for employees to request access.

```
┌──────────────────────────────────────────────────────────────┐
│                     Request Access                           │
│                                                              │
│  What system do you need access to?                          │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ 🔍  Search systems...                                   ││
│  │                                                         ││
│  │ Popular:  [Datadog]  [GitHub]  [AWS]  [Jira]            ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  What permission level?                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                    │
│  │ ○ Read   │ │ ○ Write  │ │ ○ Admin  │                    │
│  │   View   │ │  Create, │ │  Full    │                    │
│  │   only   │ │  edit    │ │  control │                    │
│  └──────────┘ └──────────┘ └──────────┘                    │
│                                                              │
│  How long do you need access?                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ 24 hours │ │ 1 week   │ │ 30 days  │ │ Custom   │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
│                                                              │
│  Why do you need this access?                                │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Investigating production latency issues...              ││
│  │                                                         ││
│  │                                                         ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ ⓘ Based on your role and this system's policy, this   │  │
│  │   request will likely need manager approval.           │  │
│  │   Estimated time: ~2 hours                             │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│              ┌──────────────────────────┐                    │
│              │   Submit Request          │                    │
│              └──────────────────────────┘                    │
└──────────────────────────────────────────────────────────────┘
```

**Design notes:**
- Light theme for employee portal
- System search is an autocomplete with popular/recent items as chips below
- Permission levels and duration use selectable cards (radio-card pattern), not dropdowns
- The predictive info box at the bottom is a subtle `--bg-subtle` panel — the system uses the policy engine to predict the likely outcome BEFORE submission
- Single primary CTA at bottom
- Conversational tone in labels ("What system do you need?") vs admin-style ("System*")

### 5. Security Dashboard — Risk Heatmap

```
┌──────────────────────────────────────────────────────────────┐
│  Security Posture                          [This Quarter ▾]  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Posture Score                                               │
│  ┌──────────────────────────────────────────────────┐       │
│  │         87 / 100          ▲ +2 from last week    │       │
│  │  ███████████████████░░░                          │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  Risk Heatmap — Systems × Permission Level                   │
│  ┌──────────────────────────────────────────────────┐       │
│  │              Read    Write    Admin    Owner     │       │
│  │  Datadog     [  ]    [  ]    [██]     [  ]      │       │
│  │  AWS         [  ]    [██]    [████]   [████]    │       │
│  │  GitHub      [  ]    [  ]    [  ]     [  ]      │       │
│  │  Okta        [  ]    [  ]    [██]     [████]    │       │
│  │  Jira        [  ]    [  ]    [  ]     [  ]      │       │
│  │                                                  │       │
│  │  Legend: [ ] Low  [██] Medium  [████] High       │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  Heatmap cells are colored:                                  │
│  Low (green-900/15%) → Med (amber-500/20%) → High (red/25%) │
│  Cell intensity = count of active grants at that risk level  │
│  Click a cell to drill down to the specific grants           │
│                                                              │
│  ┌──────────────────────────┐ ┌──────────────────────────┐  │
│  │ Stale Access (>30d idle) │ │ Policy Violations        │  │
│  │                          │ │                          │  │
│  │ 23 grants flagged        │ │ 4 active violations      │  │
│  │ [View & bulk revoke →]   │ │ [Review →]               │  │
│  │                          │ │                          │  │
│  │ Top: AWS Admin (7)       │ │ Top: Unbounded access (2)│  │
│  │      Datadog Write (5)   │ │      Missing approval (1)│  │
│  │      GitHub Admin (4)    │ │      Expired policy (1)  │  │
│  └──────────────────────────┘ └──────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

**Design notes:**
- Heatmap uses a grid of cells with background opacity varying by risk intensity
- Cells are clickable — drill down to see the actual grants
- Posture score uses a wide progress bar (8px height), color shifts from green → amber → red based on score
- "Stale Access" and "Policy Violations" are status cards with left-border accent (amber and red respectively)

---

## Interaction Patterns

### Animations & Transitions

| Interaction | Duration | Easing | Notes |
|-------------|----------|--------|-------|
| Sidebar expand | 200ms | ease-out | Label fade-in staggers 50ms after slide |
| Card hover border | 150ms | ease | Border color shift only |
| Modal open | 250ms | ease-out | Fade + scale from 0.95 → 1.0 |
| Modal close | 150ms | ease-in | Faster exit per Material guidelines |
| Slide-over panel | 300ms | cubic-bezier(0.32, 0.72, 0, 1) | Slide from right edge |
| Status badge update | 200ms | ease | Background + text color cross-fade |
| Agent pulse dot | 2000ms | ease-in-out | Opacity 1 → 0.4 → 1, infinite |
| Toast notification | Enter 200ms, exit 150ms | ease-out / ease-in | Slide down from top-right |
| Decision stream entry | 150ms | ease-out | Fade-in + translate-y from 8px |
| Table row expand | 200ms | ease-out | Height auto transition |

**Reduced motion:** All animations collapse to instant state changes when `prefers-reduced-motion: reduce` is set. The agent pulse dot switches to a static filled circle.

### Loading States

- **Page load**: Skeleton screens (not spinners) — gray rectangles with a subtle shimmer animation (2s, `--bg-elevated` → `--bg-subtle` → `--bg-elevated`)
- **Button loading**: Icon swaps to a Lucide `loader-2` with CSS spin, label text remains
- **Table loading**: Skeleton rows (5 rows) with varying widths to mimic real data
- **Decision stream**: Pulsing placeholder blocks when waiting for agent response
- **Never**: Full-page spinner, progress bar for indeterminate loads, "Loading..." text

### Empty States

Every list/table has a designed empty state:

```
┌──────────────────────────────────────────┐
│                                          │
│        [Lucide icon, 48px, muted]        │
│                                          │
│        No access requests yet            │
│        Requests will appear here when    │
│        employees submit them via the     │
│        portal or chat bots.              │
│                                          │
│        [+ Create test request]           │
│                                          │
└──────────────────────────────────────────┘
```

- Icon: relevant Lucide icon at 48px in `--text-tertiary`
- Title: Geist, text-lg, `--text-primary`
- Description: Geist, text-sm, `--text-secondary`, max-width 360px centered
- Action: `btn-secondary` with a helpful next step

---

## Chart & Data Visualization

### Library

**Recharts** for all charts (React-native, composable, good shadcn integration).

### Chart Color Palette

Do NOT use the default Recharts blue/green/orange. Use this custom palette:

```css
--chart-1: #D4930D;   /* Amber — primary data series */
--chart-2: #60A5FA;   /* Blue — secondary series */
--chart-3: #34D399;   /* Green — positive/success metrics */
--chart-4: #A78BFA;   /* Violet — tertiary series */
--chart-5: #FB923C;   /* Orange — quaternary series */
--chart-6: #F472B6;   /* Pink — if 5 aren't enough */
```

### Chart Style Rules

- **Background**: transparent (inherits card background)
- **Grid lines**: `--border` color, dashed, 1px
- **Axis text**: Geist Mono, text-xs, `--text-secondary`
- **Tooltips**: `--bg-elevated` background, `--border-strong` border, 8px border-radius, Geist Mono for values
- **No 3D effects**, no gradients under lines, no decorative elements
- **Always include**: legend (bottom, horizontally centered), axis labels with units
- **Tabular numbers** in all chart labels: `font-variant-numeric: tabular-nums`

### Chart Types Used

| Page | Chart | Type | Notes |
|------|-------|------|-------|
| Dashboard | Request volume | Area chart (7d) | `--chart-1` fill at 10% opacity |
| Dashboard | Risk distribution | Horizontal stacked bar | Green/amber/red segments |
| Agent Observatory | Confidence distribution | Histogram | Green/amber/red bars |
| Agent Observatory | Decisions over time | Multi-line chart | One line per agent type |
| Analytics | Access by system | Horizontal bar chart | Sorted descending |
| Analytics | Request resolution time | Line chart with area | p50 line + p95 shaded area |
| Security | Risk heatmap | Grid heatmap | Custom component, not Recharts |
| Security | Posture trend | Area chart (30d) | `--chart-3` with fill |

---

## Responsive Behavior

### Breakpoints

```css
--bp-sm:  640px;    /* Small phones — single column everything */
--bp-md:  768px;    /* Tablets — sidebar collapses to bottom bar */
--bp-lg:  1024px;   /* Small laptops — sidebar collapsed by default */
--bp-xl:  1280px;   /* Desktops — full layout */
--bp-2xl: 1440px;   /* Large desktops — max content width */
```

### Responsive Rules

| Component | < 768px | 768–1024px | > 1024px |
|-----------|---------|------------|----------|
| Sidebar | Bottom tab bar (5 key items) | Collapsed icon-only (always) | Collapsed, expands on hover |
| KPI cards | 2×2 grid | 4×1 row | 4×1 row |
| Data tables | Card list view (one card per row) | Horizontal scroll with frozen first column | Full table |
| Decision trail | Stacked vertically (full width) | Stacked vertically (full width) | Stacked vertically (max 800px) |
| Charts | Full width, simplified | Full width | Side-by-side in grid |
| Modal/slide-over | Full-screen sheet (bottom) | Right slide-over (400px) | Right slide-over (480px) |

### Mobile-Specific

- Bottom tab bar: 5 items max — Dashboard, Requests, Agents, Reviews, More (overflow)
- Touch targets: minimum 44x44px for all interactive elements
- Request form: full-width stacked layout, larger input heights (48px)
- Tables convert to card-list view with key info visible, expand for full row

---

## Accessibility Requirements

### WCAG 2.1 AA Compliance (minimum)

- **Contrast**: All text meets 4.5:1 against its background (verified: `--text-primary` on `--bg-root` = 12.4:1, `--text-secondary` on `--bg-root` = 4.6:1)
- **Focus**: All interactive elements have visible focus rings (`--ring` = amber at 40%, 3px offset)
- **Keyboard**: Full keyboard navigation. Tab order matches visual order. ⌘K command palette for power users.
- **Screen reader**: All status badges include screen-reader text (not just color). Agent decisions include full text descriptions. Charts have data table alternatives.
- **Motion**: All animations respect `prefers-reduced-motion`. Pulse/shimmer effects become static.
- **Color independence**: Status is never conveyed by color alone — always paired with icon + text label

### Focus Ring Style

```css
*:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px var(--ring);
  border-radius: inherit;
}
```

---

## Icon Usage

### Library: Lucide React

**Icon sizes:**
- 14px: inline with text (status, sort indicators)
- 16px: button icons, table action icons
- 20px: navigation sidebar icons
- 24px: card header icons, empty state small icons
- 48px: empty state hero icons

### Semantic Icon Map

| Concept | Lucide Icon | Context |
|---------|-------------|---------|
| Access request | `key-round` | Nav, cards, request list |
| Policy | `shield-check` | Nav, policy editor |
| System/app | `server` | Systems list |
| User | `user` | User references |
| Agent | `bot` | Agent observatory |
| Knowledge base | `book-open` | RAG documents |
| Audit log | `scroll-text` | Audit viewer |
| Risk score | `gauge` | Risk indicators |
| Approve | `check` | Action buttons |
| Deny | `x` | Action buttons |
| Expand/detail | `chevron-right` | Row expansion |
| Search | `search` | Global search |
| Settings | `settings` | Nav footer |
| Notification | `bell` | Top bar |
| Time/duration | `clock` | TTL, SLA, timestamps |
| Upload | `upload` | Document upload |
| Analytics | `bar-chart-3` | Nav, charts |
| Review | `eye` | Access review |
| Warning/alert | `alert-triangle` | Risk warnings |
| Success | `check-circle` | Status badges |
| Error | `x-circle` | Status badges |
| Pending | `clock` | Status badges |
| RAG citation | `file-text` | Source references |

---

## Anti-Patterns to Avoid

These are things that make AI-generated UIs look generic. Do not do them.

| Anti-Pattern | Why It's Bad | What to Do Instead |
|-------------|-------------|-------------------|
| Gradient hero sections | Screams "AI template" | Flat backgrounds, typography-driven headers |
| Floating blob/circle decorations | Meaningless visual noise | White space is the decoration |
| Blue-everything palette | Indistinguishable from every SaaS dashboard | Amber accent system |
| 280px always-visible sidebar | Wastes screen space, template look | 64px icon sidebar, hover-expand |
| Oversized card border-radius (16px+) | Cartoonish, loses professional edge | 8px max |
| Drop shadows on dark backgrounds | Invisible and adds visual mud | 1px borders instead |
| "AI sparkle" ✨ icons or gradient text | Cliché, dates immediately | Clean typography hierarchy |
| Progress circles/donuts for everything | Overused, poor data density | Inline bars, bullet charts |
| Gray-on-gray placeholder text | Fails contrast, looks unfinished | `--text-tertiary` at 4.5:1 minimum |
| Tabs for 2 items | Unnecessary UI chrome | Toggle or just show both |
| Accordion for short content | Hides information needlessly | Show inline |
| Modal for confirmations with no risk | Interrupts flow | Toast notification instead |
| "Are you sure?" for non-destructive actions | Approval fatigue | Reserve confirmation for revoke/delete |
