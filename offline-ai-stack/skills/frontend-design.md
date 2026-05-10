# Skill: Frontend Design

## Think first
- Which aesthetic profile applies (LUXURY / REFINED / BRUTALIST / EDITORIAL)? Pick one and commit.
- Which 3-4 shadcn primitives compose this layout? List them before opening any file.
- Am I about to introduce any of the listed anti-patterns (purple gradient, glassmorphism, emoji-as-icon)?
- How does this design hold at 375 / 768 / 1280 px — and which empty / loading / error states have I forgotten?

## Reasoning
For each UI task, work through:
1. Choose ONE aesthetic profile (LUXURY / REFINED / BRUTALIST / EDITORIAL); name it explicitly.
2. List the 3-4 shadcn primitives that compose the layout; reject re-inventions.
3. Audit candidate against the anti-pattern list before opening the editor.
4. Plan empty / loading / error states and breakpoint behavior at 375 / 768 / 1280 px.

## Anti-patterns (never produce these by default)
- Purple/blue gradient hero sections
- Glassmorphism (backdrop-blur on every card)
- Emoji used as functional icons
- Border-radius > 16px without explicit reason
- Three+ accent colors competing
- Generic "AI assistant" iconography (sparkles, magic wand)
- Drop shadows with opacity > 0.15
- Centered marketing copy by default

## Aesthetic profiles — pick exactly one and commit

LUXURY
- Headlines: serif (Playfair Display, EB Garamond)
- Body: sans (Inter, Söhne)
- Palette: monochrome + 1 jewel accent (deep emerald, oxblood, sapphire)
- Whitespace: 1.5x typical; tighten kerning on display sizes
- Imagery: editorial photography, no illustrations

REFINED (default for SaaS)
- Headlines: Inter Tight or Geist Sans, 600 weight
- Body: Inter, 400, 1.6 line-height
- 8pt grid; no arbitrary spacing
- Palette: neutral 50-900 + 1 functional accent
- Shadows: max 0.08 opacity, 4px blur

BRUTALIST
- Mono headlines (JetBrains Mono, IBM Plex Mono)
- Hard 4px shadows, offset only
- Primary RGB colors, no tints
- border-radius: 0
- Visible grid lines

EDITORIAL
- Serif body text (Source Serif, Lora)
- Multi-column layout above lg breakpoint
- Drop caps, footnote markers
- Pull quotes with rule-line treatment

## Stack defaults
- Components: shadcn/ui — do not reinvent
- Styling: Tailwind tokens only; no arbitrary `[#hex]` values
- Icons: lucide-react, single weight, single size scale
- Motion: framer-motion, easing `[0.16, 1, 0.3, 1]`, duration ≤ 300ms
- Forms: react-hook-form + zod

## Process
1. State which aesthetic profile applies.
2. List the 3-4 components from shadcn that compose the layout.
3. Build mobile-first; verify at 375 / 768 / 1280.
4. Run through the anti-pattern list as a self-check before returning.
