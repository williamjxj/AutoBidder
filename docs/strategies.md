# Strategies - User Guide

Last Updated: March 2026

Strategies define how AI should shape proposal tone, structure, and persuasion style.

## What Strategies Control

- Writing tone (professional, technical, concise, etc.)
- Prompt instructions and style constraints
- Default strategy selection for generation flows

## Core Features

- List strategies (`GET /api/strategies`)
- Create strategy (`POST /api/strategies`)
- Update strategy (`PATCH /api/strategies/{id}`)
- Delete strategy (`DELETE /api/strategies/{id}`)
- Set default (`POST /api/strategies/{id}/set-default`)

## Recommended Workflow

1. Create 2-3 distinct strategies (for example: Technical Deep-Dive, Fast Close, Executive Summary).
2. Set one as default for daily usage.
3. Compare proposal outcomes and iterate wording.
4. Keep prompts specific and measurable.

## Prompt Writing Tips

- Do: include target audience and expected length.
- Do: specify must-have sections (opening, solution, timeline, CTA).
- Do not: over-constrain with conflicting instructions.
- Do not: include vague phrases like "make it better" without criteria.

## Troubleshooting

- Generated text ignores style:
  - Verify selected strategy is active/default.
  - Reduce conflicting instructions between strategy and form notes.
- Results too generic:
  - Add concrete differentiators and proof points in the strategy prompt.

## Related Docs

- [proposals.md](./proposals.md)
- [analytics.md](./analytics.md)
- [dashboard.md](./dashboard.md)
