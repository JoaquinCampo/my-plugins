---
name: artifact
description: Use when building or improving HTML/CSS artifacts, React pages, dashboards, landing pages, explainers, demos, SVG diagrams, UI prototypes, or visual outputs where design quality, subject-specific treatment, responsive behavior, and render verification matter.
---

# Artifact

Use this skill to turn visual output into a deliberately designed artifact, not a generic generated page. It applies to polished documents, dashboards, tools, landing pages, demos, games, and visual explanations.

## First Classify The Treatment

Pick the treatment before choosing style:

- **Document**: memo, plan, report, narrative explainer. Prioritize typography, hierarchy, whitespace, and readable structure. Avoid giant heroes.
- **Dashboard or tool**: scanned and operated repeatedly. Prioritize information density, state encoding, stable controls, and fast comparison.
- **Landing or editorial page**: public-facing or shareable. Use a strong first impression, visual assets, and one memorable aesthetic decision.
- **Component or app surface**: fit the existing product system first, then refine hierarchy, interaction states, and empty or loading states.
- **Conceptual explainer**: use diagrams, SVG, canvas, code, or animation to make the idea inspectable.

Completion criterion: the chosen treatment is explicit in the design plan and the output matches that treatment.

## Start With The User Mental Model

Before layout or visuals, define what the viewer should understand at a glance:

- **Viewer**: who is looking at this and what pressure they are under.
- **Question**: the first question the artifact must answer.
- **Action**: what the viewer can decide, do, or inspect next.
- **Evidence**: the reason, source, state, or tradeoff that makes the action trustworthy.
- **Depth path**: what belongs in the first view versus what belongs lower on the page, in a detail panel, or behind interaction.

Write the artifact from the viewer's side of the screen. Users do not care how the system works behind the scenes unless that mechanism changes trust, timing, risk, or accountability.

For operational explainers, prefer this order:

1. What needs attention.
2. Who owns it.
3. Why it matters.
4. Where to act.
5. What happened after action.

Completion criterion: the first viewport communicates the artifact's core idea without requiring a reader to understand implementation internals.

## Design Plan Before Code

Before writing UI code, produce a compact plan:

- **Subject**: the concrete subject, audience, and single job of the artifact.
- **Color**: 4 to 6 named hex values, including chosen neutrals and semantic state colors if needed.
- **Type**: display, body, and utility or data roles. Use the existing product font stack when one exists.
- **Layout**: one or two sentences explaining composition, density, and responsive behavior.
- **Visual system**: the main visual device, for example SVG diagram, data cards, product imagery, map, timeline, canvas scene, or typographic treatment.

Then build from that plan. If a later design decision contradicts the plan, revise the plan first.

## Respect Existing Systems

Precedence is:

1. User's explicit direction.
2. Existing project design system, tokens, components, and framework conventions.
3. This skill's guidance.
4. New visual invention.

When a project already has a UI system, reuse its tokens, components, icons, layout primitives, and state conventions. Add new visual language only where the existing system has no answer.

## Use SVG When It Clarifies Complex Ideas

SVG is the right tool when the artifact needs inspectable, precise, scalable meaning:

- Systems diagrams, architecture maps, process flows, timelines, dependency graphs, funnels, matrices, and conceptual maps.
- Labeled spatial relationships, arrows, callouts, annotations, and layered explanations.
- Lightweight charts, gauges, sparklines, badges, custom icons, and symbolic visual language.
- Interactive explainers where hover or click should reveal semantic parts of a diagram.

Build SVGs with meaningful structure:

- Use `viewBox`, grouped layers, labels, titles, descriptions, and readable ids or classes.
- Keep text real text when it should be selectable, searchable, or accessible.
- Use `<title>` and `<desc>` where the SVG carries important meaning.
- Prefer simple shapes, lines, paths, markers, masks, and patterns over opaque generated path soup.
- Put repeated values in CSS variables or shared classes.
- Make diagrams responsive with preserved aspect ratio and container constraints.

Do not avoid SVG just because it is visual code. Use it when it is the clearest representation of the idea.

Use Canvas or WebGL instead when the visual is high-volume, generative, particle-based, heavily animated, or performance-sensitive. Use HTML/CSS for ordinary layout and controls.

Completion criterion: every SVG has a clear semantic reason to exist, no unreadable long path data unless unavoidable, and it remains legible at mobile and desktop widths.

## Efficient SVG Iteration Loop

SVGs fail when they are only technically valid. Treat complex SVG as an interface, not decoration.

Use this loop for system maps, flows, architecture diagrams, timelines, or dense conceptual visuals:

1. **Name the reader journey** in plain language, for example "prompt, route, review, decide, record."
2. **List the semantic objects** before drawing, including actors, states, decisions, evidence, actions, and hidden support layers.
3. **Assign visual priority**: primary user-facing objects are largest and highest contrast; implementation support is smaller, lower contrast, or lower on the canvas.
4. **Block the SVG first** with boxes, circles, labels, and arrows. Do not tune paths, gradients, or ornament until the reading order works.
5. **Render early** at desktop and mobile sizes. Inspect screenshots for clipped text, crossing connectors, tiny labels, and whether the first read is obvious.
6. **Patch one layer at a time**: text fit, then object spacing, then connectors, then color, then polish. Avoid rewriting the whole SVG unless the mental model is wrong.
7. **Keep a mobile strategy**: simplify, stack, or allow horizontal scroll for complex diagrams. Do not shrink dense SVG until labels become unreadable.

Prefer real text, grouped layers, reusable classes, and short connector paths. Use curved connectors only when they improve reading order. If the diagram contains a user-facing workflow, make the user-facing surface visually dominant and make backend machinery secondary.

Completion criterion: after desktop and mobile screenshots before completion, the SVG explains the idea at a glance, has no clipped text or collisions, and still preserves enough detail for inspection.

## Avoid Generic AI Aesthetics

Avoid defaulting to:

- Warm cream plus serif plus terracotta.
- Purple or blue gradient hero on white.
- Near-black plus one neon accent.
- Everything centered.
- Emoji as section markers.
- `rounded-lg` everywhere.
- Accent rails on rounded cards.
- Inter, Space Grotesk, or system fonts as the automatic answer when no product system requires them.
- Decorative numbered markers unless the content is genuinely sequential.

If the user explicitly asks for one of these, follow the user. Otherwise spend design freedom on subject-specific choices.

## Frontend Rules For Codex

- Build the actual usable experience as the first screen for apps, tools, and games. Do not create a marketing landing page unless requested.
- Keep dashboards quiet, dense, and operational. Avoid oversized hero sections and decorative card grids.
- Use cards only for repeated items, modals, or genuinely framed tools. Do not put cards inside cards.
- Use icons for tool buttons when an icon is more recognizable than text.
- Use stable dimensions for boards, controls, counters, tiles, charts, and SVG canvases so hover states and dynamic labels do not shift layout.
- Do not scale font size with viewport width. Use fixed type scales and responsive layout instead.
- Keep letter spacing at `0` except for small uppercase labels.
- Avoid one-note palettes. Semantic state colors do not count as the accent.
- Ensure text never overlaps adjacent content or escapes controls.

## Copy Rules

Write from the user's side of the screen:

- Controls say what happens.
- Errors explain what went wrong and what to do next.
- Labels use domain language, not implementation language.
- Specific beats clever.
- Use real content. Never use lorem unless the user asks for placeholder copy.

## Gotchas

- **Technically valid is not visually successful**: passing HTML, CSS, or SVG checks does not mean the artifact communicates. Render it and inspect the actual first read.
- **Implementation diagrams often bury the user**: if the artifact explains a workflow, make user-facing objects dominant and push machinery into a quieter support layer.
- **Dense SVGs collapse on mobile**: choose stacking, simplification, or horizontal scroll before shrinking labels until they are unreadable.
- **Generic polish hides weak structure**: shadows, gradients, and rounded cards cannot fix a missing mental model, unclear action, or weak evidence path.

## Verification Before Completion

For static HTML that can open directly, verify the file exists and inspect it in browser when feasible.

For apps or components, run the dev server when feasible and verify with browser screenshots:

- Desktop viewport.
- Mobile viewport.
- No body horizontal scroll.
- No obvious text overlap or clipped controls.
- SVGs and visual assets render nonblank and stay framed.
- Interactive controls, hover states, or toggles work for the main flow.
- Motion respects `prefers-reduced-motion` when motion is significant.

If browser verification is unavailable, state that limitation and run the strongest available static checks, such as lint, build, typecheck, or targeted HTML/CSS inspection.

Completion criterion: the artifact is implemented, visible, responsive, and checked against the treatment and visual plan.
