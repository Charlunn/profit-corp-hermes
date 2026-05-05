# Technical Specification: Found in the PyTorch Lightning AI Training Library ( semgrep.dev ) points by j12
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
- **Build Time**: 22
- **Shared Shortlist Source**: `assets/shared/external_intelligence/triage/prioritized_signals.json`
- **Chosen Idea ID**: IDEA-001
