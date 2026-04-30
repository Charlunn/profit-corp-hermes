# Technical Specification: . Intel Arc Pro B70 Review ( pugetsystems.com ) points by zdw hide . Who owns th
- **Stack**: Hermes prompts + Python triage/read-model pipeline + markdown shared-state artifacts
- **File Tree**:
  ```
  scripts/triage_external_signals.py
  scripts/generate_role_handoffs.py
  scripts/run_signal_analysis_loop.sh
  assets/shared/external_intelligence/triage/prioritized_signals.json
  assets/shared/PAIN_POINTS.md
  assets/shared/MARKET_PLAN.md
  assets/shared/TECH_SPEC.md
  assets/shared/CEO_RANKING.md
  ```
- **MVP Features**: deterministic triage, shared shortlist generation, role-specific markdown handoffs, CEO ranking over the same shortlist
- **Build Time**: 10
- **Shared Shortlist Source**: `assets/shared/external_intelligence/triage/prioritized_signals.json`
- **Chosen Idea ID**: IDEA-001
