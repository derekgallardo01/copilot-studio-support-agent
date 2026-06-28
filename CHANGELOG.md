# Changelog

Notable changes to the Copilot Studio support agent kit. Dates are when the
change landed on `main`.

## 2026-06-27 — Docker support
- Dockerfile so the kit runs via `docker run` without a Python install
- README "Run in Docker" section with the common invocations

## 2026-06-27 — Second worked corpus
- `sim/data-saas/` (product features / billing FAQ / troubleshooting) — proves
  the agent isn't just for HR/IT/Security
- `evals/golden-saas.json` — 14 cases including escalations
- `evals/run.py` now accepts positional args for the golden file + docs folder
- CI runs both eval sets on every push

## 2026-06-27 — GitHub Actions CI
- `.github/workflows/ci.yml` running pytest + eval + smoke-test on Python 3.11
- CI status badge added to README

## 2026-06-27 — Build-out: multi-turn conversation, evals, docs
- Multi-turn `Conversation` wrapper with smart context injection (only
  re-runs with prior context when the bare query is uncertain)
- `evals/golden.json` (16 cases) + `evals/run.py` with CI-gating exit code
- `sim/cli.py` interactive REPL with `reset` / `quit` commands
- 4 new tests covering conversation behaviour
- `docs/architecture.md`, `customization.md`, `evaluation.md`
- `docs/sample-run.txt` (UTF-8 captured single + multi-turn output)
- README rewritten with architecture, sample, eval, customization sections
- Fixed pre-existing Windows cp1252 crash in `sim/run.py`

## 2026-06-27 — Initial public release
- Offline Copilot Studio agent simulator with TF-IDF retrieval, sensitive-
  topic + low-confidence escalation, source-cited grounded answers
- Declarative `agent-template/` (YAML + topics + prompt library) for Copilot Studio
- `deploy-guide.md` for the tenant build
- 5 unit tests
