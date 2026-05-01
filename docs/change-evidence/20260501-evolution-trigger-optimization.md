# 2026-05-01 Evolution Trigger Optimization

## Goal
Turn runtime self-evolution prompting from fixed template output into evidence-driven trigger evaluation so the repository can automatically surface optimization pressure from real gate, source, host-feedback, target-effect, and AI-coding-experience signals.

## Risk
- risk_tier: medium
- primary_risk: auto-detected trigger states could misclassify stale or incomplete evidence and either suppress needed follow-up work or create noisy evolution prompts
- compatibility_boundary: this change updates selector and evaluator scripts plus tests; it does not auto-apply rules, enable skills, sync target repos, push, merge, or mutate active policy

## Changes
- updated [Runtime Evolution Evaluator](/D:/CODE/governed-ai-coding-runtime/scripts/evaluate-runtime-evolution.py) to load real evidence from current-source compatibility, host feedback summary, target repo effect feedback, and AI coding experience review
- updated [Next-Work Selector](/D:/CODE/governed-ai-coding-runtime/scripts/select-next-work.py) so omitted `gate_state`, `source_state`, and `evidence_state` are auto-detected from repository facts instead of falling back directly to static defaults
- updated [Runtime Evolution Tests](/D:/CODE/governed-ai-coding-runtime/tests/runtime/test_runtime_evolution.py) to require dynamic evidence snapshots and dynamic candidate ids
- updated [Autonomous Next-Work Selector Tests](/D:/CODE/governed-ai-coding-runtime/tests/runtime/test_autonomous_next_work_selection.py) to cover fail-closed auto-detection and explicit-state override behavior

## Verification
```powershell
python -m unittest tests.runtime.test_runtime_evolution
```

Result: pass. Key output: `Ran 7 tests`, `OK`.

```powershell
python -m unittest tests.runtime.test_autonomous_next_work_selection
```

Result: pass. Key output: `Ran 7 tests`, `OK`.

```powershell
python scripts/evaluate-runtime-evolution.py --as-of 2026-05-01
```

Result: pass. Key output: dynamic `candidate_count=4`, `evidence_snapshot` present, and candidates now include `EVOL-HOST-FEEDBACK`, `EVOL-EFFECT-FEEDBACK`, `EVOL-AI-EXPERIENCE`, and `EVOL-SOURCE-COLLECTOR`.

```powershell
python scripts/select-next-work.py --as-of 2026-05-01
```

Result: pass. Key output: `auto_detected_inputs` present with `gate_state=pass`, `source_state=fresh`, `evidence_state=fresh`, and `next_action=defer_ltp_and_refresh_evidence`.

## Outcome
- self-evolution prompts are now tied to real repository evidence instead of only fixed candidate templates
- next-work selection now shows why its state is `pass/fresh/fresh` or fail-closed, rather than silently trusting static defaults
- target-effect backlog candidates and AI coding proposals now surface as first-class evolution signals

## Rollback
- revert `scripts/evaluate-runtime-evolution.py` and `scripts/select-next-work.py`
- revert `tests/runtime/test_runtime_evolution.py` and `tests/runtime/test_autonomous_next_work_selection.py`
- remove this evidence file if the trigger optimization slice is rolled back
