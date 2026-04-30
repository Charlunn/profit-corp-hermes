# Project Rules

## Frontend UI/UX skill enforcement

This rule applies only to frontend development work.

When a request involves frontend page implementation, visual redesign, component styling, layout work, interaction design, accessibility polish, or any user-facing web/mobile interface changes handled by frontend developers, you MUST invoke the `/ui-ux-pro-max` skill before proposing code changes or implementation steps.

Required behavior:
- Start frontend UI work with `/ui-ux-pro-max` to generate or review the design system first.
- Use the skill's design-system output as the source of truth for layout, typography, color, spacing, responsiveness, accessibility, and interaction details.
- If the task is implementation-only but touches user-facing frontend UI, still invoke `/ui-ux-pro-max` first to validate the intended UX direction before coding.
- If the installed skill is missing, restore it using `uipro init --ai claude` from the project root before continuing frontend UI work.

This rule does not apply to non-frontend roles unless the user explicitly asks them to perform frontend UI work.
