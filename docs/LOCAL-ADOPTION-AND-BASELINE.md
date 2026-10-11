# LACE Local Adoption and Baseline

> Local working document for `Aashuthosh10/LACE`. This is not upstream-approved source documentation. It records the migration and verification performed on 2026-10-11 (Asia/Calcutta) and remains pending owner review.

## Source of truth and repository state

- Canonical repository: `https://github.com/Aashuthosh10/LACE.git`
- Upstream branch inspected: `main`
- Exact base commit: `95823e8db6b9cb1dfa88216d9d9612ca051491e9`
- Local branch: `codex/source-migration-baseline`
- Local clone: `<local clone path>`
- Original standalone scaffold: `<original standalone scaffold path>`; it was preserved and not merged or overwritten.

The authoritative team repository's instructions, source, tests, milestone documents, and acceptance gates supersede the old personal Sprint 0 scaffold. During the initial baseline, only local documentation was added. The later recovery changes are listed in the recovery sections below and remain uncommitted pending owner review.

## Environment and setup

Initial baseline environment:

- Windows PowerShell
- Python 3.13.14 (`py -0p` showed Python 3.13)
- Git 2.51.0.windows.1
- Docker CLI 28.3.3, context `desktop-linux`
- `uv`: unavailable on PATH
- Docker Linux daemon: unavailable during the initial baseline; the Docker Desktop Linux engine pipe was not present
- Approved image `lace-pytest:3.12-v1`: not inspectable during the initial baseline because the daemon was unavailable
- Available C: drive space at inspection: approximately 103 GB

Because `uv` was unavailable, the declared environment was installed in the ignored local `.venv` with the equivalent command:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e . "pytest>=8.3,<10" "ruff>=0.9,<1"
```

Installation succeeded. No global packages were installed and `uv.lock` was not modified.

## Capability map

| Capability | Implementation | Tests / local evidence | State and boundary |
|---|---|---|---|
| Package and Typer CLI | `src/lace/cli.py`, `src/lace/config.py` | CLI tests; help/version/startup commands | Implemented and locally runnable |
| Diagnostics / doctor | `src/lace/diagnostics.py` | `lace doctor`, `doctor --json` | Implemented; local result reports Docker `verified=false` and Ollama unavailable |
| Repository identity and scanning | `src/lace/repository/` | `tests/test_repository.py`; disposable scan command | Implemented; read-only Git-tracked inventory with exclusions and bounds |
| Context selection | `src/lace/context/` | `tests/test_context.py`; disposable scan command | Implemented; deterministic bounded selection |
| Patch parser | `src/lace/patches/parser.py` | `tests/test_parser.py` | Implemented; untrusted diff parsing only |
| Forbidden-path policy | `src/lace/patches/policy.py` | `tests/test_policy.py` | Implemented; deterministic policy authority |
| Validator / Git applicability | `src/lace/patches/validator.py` | `tests/test_validator.py`; local validation | Initial Windows applicability failure recovered with CRLF-aware patch transport; later validation passed |
| Advisory risk assessment | `src/lace/risk.py`, `src/lace/patches/assessment.py` | `tests/test_risk.py` | Implemented; advisory and separate from policy |
| Disposable workspace | `src/lace/workspace/` | `tests/test_workspace.py` | Initial positive patch-application tests failed during baseline; later recovery verification passed and preserved the original |
| Restricted Docker executor | `src/lace/execution/` | `tests/test_execution.py`, `tests/test_execution_live.py` | Implemented fail-closed adapter; later local verification passed all eight Docker-live probes through `DockerExecutor` |
| Interactive terminal | `src/lace/interactive.py`, `src/lace/terminal/` | `tests/test_interactive.py`; `/exit` probe | Implemented; safe deterministic commands only |
| JSON output | CLI `--json` options and model `to_dict()` methods | CLI tests and doctor/scan probes | Implemented for current commands |
| Ollama/model integration | No model module or gateway | Doctor reports Ollama unavailable | Not implemented; M5 candidate |
| Autonomous repair | No repair coordinator | No implementation | Not implemented; M6 |
| Human approval/final apply | No approval/apply-to-original workflow | No implementation | Not implemented; M6 |
| Benchmark/evaluation | No benchmark runner/reporting engine | No implementation | Not implemented; M7 |

## Commands and results

The documented commands were run through the local `.venv` equivalent of `uv run`.

| Command | Result | Evidence |
|---|---:|---|
| `lace --help` | exit 0 | Typer command list displayed |
| `lace --version` | exit 0 | `lace 0.1.0` |
| `lace doctor` | exit 0 | Python/Git ready; Ollama unavailable; isolation unverified |
| `lace doctor --json` | exit 0 | `m4_ready: false`, error `Docker Linux engine is unavailable` |
| `lace` interactive startup with `/exit` | exit 0 | Session opened and closed cleanly |
| `lace scan --repo <disposable fixture> --task ... --json` | exit 0 | 4 tracked files, 2 Python files, deterministic selection |
| `lace validate <patch> --repo <disposable fixture> --json` | exit 5 | Policy allowed, Git applicability failed, original unchanged |
| `lace workspace apply <patch> --repo <disposable fixture> --json` | exit 4 | Workspace cleaned; applicability failed; original unchanged |
| `lace test <patch> --repo <disposable fixture> --json` | exit 6 | No tests run because workspace patch application failed |

The fixture repository was created outside the team clone and remained unchanged after the commands. The patch applicability failure was also reproduced in the test suite. Direct `git apply --check` against the disposable fixture passed, so the discrepancy needs investigation in the workspace-copy/application path before claiming M3 positive verification on this machine.

## Baseline quality results

Full baseline:

```text
python -m pytest
88 collected; 73 passed, 15 failed; exit code 1
```

The 15 failures comprised 7 non-live failures and 8 Docker live failures.

Non-live baseline:

```text
python -m pytest -m "not docker_live"
80 selected, 8 deselected; 73 passed, 7 failed; exit code 1
```

The non-live failures were:

- `tests/test_cli.py::test_workspace_apply_json`
- `tests/test_repository.py::test_rejects_subdirectory_and_non_repository`
- `tests/test_validator.py::test_rejects_non_git_directory`
- `tests/test_workspace.py::test_applies_in_workspace_cleans_up_and_preserves_original`
- `tests/test_workspace.py::test_unexpected_workspace_change_fails_closed`
- `tests/test_workspace.py::test_cleanup_error_is_reported`
- `tests/test_workspace.py::test_repeated_operations_preserve_repository`

The workspace-related failures reported `Git rejected patch applicability: error: patch failed: calculator.py:1`. The repository/validator failures expected `Git work tree` while the implementation reports `Git work-tree root`.

Live baseline:

```text
python -m pytest -m docker_live
8 selected, 80 deselected; 8 failed; exit code 1
```

All live executor tests failed because the Docker Linux engine was unavailable. The adapter returned `environment_error` with `Docker Linux engine is unavailable`; one live probe attempted `docker ps` and received the same daemon connection failure. No host pytest fallback was used.

Quality checks:

```text
python -m ruff format --check .
63 files already formatted; exit code 0

python -m ruff check .
All checks passed; exit code 0
```

## Upstream status versus local verification

The README and traceability documents state that M4 was accepted in a recorded Docker Desktop Linux environment. The initial Windows baseline below was not evidence of local M4 because Docker was unavailable at that time. A later local verification provisioned the approved image and independently passed all eight Docker-live tests through `DockerExecutor`; M4 is now locally verified for the current machine.

The code and tests show meaningful M1-M4 implementation. M5 Ollama integration is not implemented and has not been started.

## Milestone rebaseline

The upstream sequence is canonical:

1. M1 — Python foundation and deterministic patch validation
2. M2 — Repository scanning and context selection
3. M2.5 — Interactive terminal interface
4. M3 — Safe workspace and patch processing
5. M4 — Restricted pytest execution
6. M5 — Ollama integration
7. M6 — Bounded test-driven repair with explicit approval/final apply
8. M7 — Benchmarking and evaluation
9. M8 — Hardening, final testing, and demonstration

The former personal Sprint 0 overlaps mainly with M1 foundation, but it is historical context, not a competing upstream milestone. Its minimal configuration/CLI/logging ideas were superseded by the team's Typer/Pydantic/modular implementation.

M5 is the expected next feature milestone from the upstream plan, but it remains pending explicit owner approval. No M5 implementation was started here.

## Risks, limits, and deferred work

- The initial baseline was blocked by an unavailable Docker daemon and approved image; this was later resolved for local M4 verification.
- The initial Windows workspace patch-applicability failure was resolved by the CRLF-aware patch transport recovery.
- Two negative tests have message expectation mismatches (`Git work tree` versus `Git work-tree root`).
- Doctor's human output labels Docker as `ready` based on CLI presence even though JSON correctly reports `verified: false`; this is a documentation/UI clarity risk.
- Ollama, repair, approval/final apply, rollback restoration, and benchmarking remain deferred.
- A copy-only workspace is not a security sandbox; untrusted tests were never run on the host.

## Old scaffold disposition

The previous scaffold remains untouched in its original directory. No files were transplanted, merged, reset, or deleted. Future work should use this team clone and upstream milestone documents as the source of truth.

## Checkpoint

This feature branch contains the local working report and the uncommitted recovery changes listed below. It is awaiting owner review. No commit, push, pull request, tag, or remote change was made.

## Recovery addendum — 2026-10-11

The baseline investigation reproduced all seven non-live failures before editing. Five shared a real cross-platform defect: `Path.read_text()` normalized an LF patch while copied Windows workspace files retained CRLF, so Git rejected patch context. Two assertions expected `Git work tree` while the documented implementation error was `Git work-tree root`; those were stale test expectations, not a product behavior defect.

The minimal recovery added `src/lace/patches/line_endings.py`, which rewrites a patch to CRLF only when all existing patch targets are CRLF. Both validator and workspace application use this adapter. It preserves LF behavior and does not weaken policy, risk separation, workspace integrity, or subprocess argument handling. The two stale assertions were aligned to the existing `Git work-tree root` contract. A CRLF validator regression test was added.

After the fixes:

```text
python -m pytest tests/test_validator.py tests/test_workspace.py tests/test_cli.py tests/test_repository.py
38 passed in 27.68s; exit code 0

python -m pytest -m "not docker_live"
81 passed, 8 deselected in 29.19s; exit code 0

python -m ruff format --check src tests
48 files already formatted; exit code 0

python -m ruff check src tests
All checks passed; exit code 0
```

The disposable fixture then produced `validate` exit 0 and `workspace apply` exit 0, with `original_unchanged: true`, `workspace_cleaned: true`, and `calculator.py` as the only changed workspace target. The `test` command returned exit 6 with `environment_error` because the Docker daemon was reachable but `lace-pytest:3.12-v1` was not installed. No image was pulled or built.

Recovery source/test changes:

- `src/lace/patches/line_endings.py` — shared CRLF/LF patch transport adapter.
- `src/lace/patches/validator.py` — use workspace-aware patch bytes.
- `src/lace/workspace/processor.py` — use workspace-aware patch bytes.
- `tests/test_validator.py` — correct the stale error expectation and add CRLF regression coverage.
- `tests/test_repository.py` — correct the stale error expectation.

The local branch remains uncommitted and awaits owner review. This recovery evidence records the earlier missing-image state; the later verification section records the current M4 result.

## Final M4 verification

The later local verification used the provisioned `lace-pytest:3.12-v1` image and the existing restricted executor. Results were:

```text
89 collected
81 non-Docker tests passed
8 Docker-live tests passed through DockerExecutor
Ruff format --check passed
Ruff check passed
git diff --check passed
```

The Docker-live probes covered network and filesystem isolation, non-root identity, resource limits, timeout and cleanup behavior, bounded output, concurrent container naming, applied container controls, and original-repository preservation. M4 is locally verified on the current machine. M5 remains unimplemented and requires explicit owner approval.
