# Shipwright — Design Direction

## Three Initial Directions

### Theme Name: Evidence Ledger
Very Brief Intro: A quiet, forensic interface inspired by lab notebooks and audit trails. It makes software quality feel inspectable, calm, and trustworthy rather than flashy.
Probability: 0.07

### Theme Name: Release Control Room
Very Brief Intro: A high-contrast operations console for maintainers shipping under pressure. Dense telemetry, decisive status color, and command-center hierarchy make readiness feel actionable.
Probability: 0.04

### Theme Name: Editorial Maintainer
Very Brief Intro: A publication-like product surface that treats repository health as a living editorial artifact. Strong typography and asymmetric composition turn technical evidence into a readable narrative.
Probability: 0.08

## Chosen Direction: Evidence Ledger

### Design Movement
Swiss International Style crossed with forensic information design: disciplined typography, visible structure, restrained color, and evidence presented as a sequence of verifiable observations.

### Core Principles
1. **Evidence before decoration:** every visual hierarchy should answer what was checked, what was found, and what action follows.
2. **Quiet confidence:** use a warm paper-like canvas, ink-dark type, and one signature signal color instead of gradients or neon.
3. **Asymmetric editorial rhythm:** combine a narrow rail, a wide evidence canvas, and offset panels rather than centering every block.
4. **Progressive disclosure:** show the decision first, then the score, then the evidence path and remediation detail.

### Color Philosophy
The base is a warm mineral white with ink-black typography to evoke a printed engineering dossier. The signature color is **Shipwright Copper** (`#C65D38`), used sparingly for active decisions, change markers, and the moment a check needs human attention. Moss green communicates verified evidence; muted slate communicates context; rust communicates a release blocker. The palette should feel durable and operational, not like a generic SaaS dashboard.

### Layout Paradigm
A persistent left rail behaves like a document index. The main view is an asymmetric two-column evidence desk: a broad narrative/report area and a narrow decision column. Cards should be rectangular dossier sheets with selective borders and small corner labels, not a uniform grid of rounded boxes. The visual anchor is a timeline/ledger of checks that reads top-to-bottom.

### Signature Elements
1. A copper **keel line** running through the readiness timeline, connecting checks like a ship blueprint.
2. Small uppercase **evidence stamps** showing source paths, commands, and timestamps.
3. A compact **release signal** that changes from moss to copper/rust as evidence changes, rather than a generic progress ring.

### Interaction Philosophy
Interactions should feel like examining a record: selecting a check reveals its evidence without losing the overall report, filters update instantly, and every action explains its consequence. No mystery buttons. Keyboard navigation and visible focus states are first-class because maintainers often work from terminals and code review contexts.

### Animation
Use short 160–220ms transitions with a sharp ease-out. The readiness signal should settle like a stamp, not bounce. Ledger rows reveal with a 35ms stagger only on initial load; subsequent filtering is instant. Evidence drawers slide from the right with opacity and translate only. Respect reduced motion and never animate layout dimensions.

### Typography System
Use **IBM Plex Sans** for body and controls and **IBM Plex Mono** for evidence, commands, paths, timestamps, and scores. Headings use IBM Plex Sans 700 with tight tracking; eyebrow labels use mono 11px uppercase with letter spacing. Avoid Inter and avoid oversized marketing headlines. The hierarchy is: 12px evidence metadata, 14px controls, 16px body, 22px section titles, 44–56px readiness verdict.

### Brand Essence
Shipwright is the local-first release-readiness instrument for maintainers who want proof before they publish; it is different because every verdict is backed by inspectable evidence. Personality: **forensic, calm, dependable**.

### Brand Voice
Headlines are decisive and concrete. CTAs describe an action and its evidence outcome. Microcopy explains what happened, never congratulates vaguely.

Example lines:
- “Know what is ready before the tag exists.”
- “Inspect 18 checks · 16 verified · 2 need attention.”

### Wordmark & Logo
The mark is a geometric ship keel built from three descending vertical ribs, forming an abstract `S` through negative space. The wordmark uses a custom-feeling condensed lockup: SHIP in bold sans, WRIGHT in mono with a copper rule beneath. The mark must work alone as a favicon and beside the name in the rail.

### Signature Brand Color
**Shipwright Copper — `#C65D38`**. It owns the moment where raw repository evidence becomes a release decision.

## Style Decisions
- Do not use purple gradients, generic hero illustrations, or all-rounded SaaS cards.
- Keep the main experience as a maintainer dashboard/report viewer, not a marketing landing page.
- Use the generated brand mark only for the header/fav icon; use generated imagery sparingly and never as filler.
- The UI is a demonstrative report viewer in the static frontend; the real CLI contract will be documented and implemented in the repository layer.
