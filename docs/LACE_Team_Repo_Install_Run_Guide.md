# LACE Team Repository Install and Run Guide

This guide is a local working guide for the team repository. Commands marked **executed locally** were run on Windows PowerShell on 2026-10-11. Commands marked **documented/unrun** come from repository documentation but were not run because the required tool or safe environment was unavailable.

## Prerequisites

Required by the repository:

- Python 3.12 or newer
- Git 2.40 or newer
- `uv` for the preferred environment workflow
- Docker Desktop/Linux engine and the administrator-provisioned approved image for M4 test execution

Observed machine during the initial baseline:

- Python 3.13.14 — available and used
- Git 2.51.0.windows.1 — available and used
- `uv` — unavailable on PATH
- Docker CLI 28.3.3 — available
- Docker Linux daemon — unavailable during the initial baseline
- `lace-pytest:3.12-v1` — not inspectable during the initial baseline because the daemon was unavailable

Later M4 verification status:

- Docker Linux engine — available
- `lace-pytest:3.12-v1` — provisioned and verified
- Docker-live suite — 8 passed through the approved `DockerExecutor`

## Safe clone and directory selection

Keep the old scaffold untouched. Clone the team repository into a new sibling directory:

```powershell
Set-Location <parent-directory>
git clone https://github.com/Aashuthosh10/LACE.git LACE-team
Set-Location .\LACE-team
git switch -c codex/source-migration-baseline
```

**Executed locally:** clone, branch creation, and source inspection. Base commit was `95823e8db6b9cb1dfa88216d9d9612ca051491e9`.

## Preferred setup with uv

**Documented/unrun because `uv` was unavailable:**

```powershell
uv sync --dev
uv run lace --help
```

## Equivalent setup used locally

The equivalent was installed only into the ignored clone-local virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e . "pytest>=8.3,<10" "ruff>=0.9,<1"
```

Installation succeeded. `uv.lock` was not changed.

Use the local executable form for the remaining commands when `uv` is unavailable:

```powershell
$lace = '.\.venv\Scripts\lace.exe'
$python = '.\.venv\Scripts\python.exe'
```

## Basic CLI

**Executed locally:**

```powershell
& $lace --help
& $lace --version
& $lace doctor
& $lace doctor --json
```

All exited `0` during the initial baseline. Doctor then reported Python and Git ready, Ollama unavailable, and Docker isolation `verified: false` with `Docker Linux engine is unavailable`. That was an earlier environment result; it does not represent the later M4 verification state.

The documented bare startup is interactive. **Executed locally** with `/exit` piped to the process:

```powershell
'/exit' | & $lace interactive --repo <disposable-fixture>
```

It exited `0` and closed the session cleanly. Natural-language input does not invoke AI.

## Disposable fixture workflow

Use a disposable Git fixture, never the team repository or an arbitrary user repository. The documented command categories are:

```powershell
& $lace scan --repo <fixture> --task "Fix incorrect discount calculation" --json
& $lace validate <patch> --repo <fixture> --json
& $lace workspace apply <patch> --repo <fixture> --json
& $lace test <patch> --repo <fixture> --json
```

**Executed locally:** scan succeeded. Validate and workspace apply reached the safety checks but failed Git applicability for the fixture patch; both reported the original unchanged. `test` did not run tests because workspace application failed. No host pytest fallback was used.

## Quality checks

**Executed locally:**

```powershell
& $python -m pytest
& $python -m ruff format --check .
& $python -m ruff check .
```

Initial baseline results: 88 collected, 73 passed, 15 failed; Ruff format passed; Ruff check passed. The seven non-live failures and eight Docker-live failures are recorded in `LOCAL-ADOPTION-AND-BASELINE.md` as historical evidence.

To separate the environment-sensitive suite:

```powershell
& $python -m pytest -m "not docker_live"
& $python -m pytest -m docker_live
```

The initial baseline produced 73 passed/7 failed non-live and 8 failed live because Docker was unavailable. The later verification produced 81 passed non-live and 8 passed Docker-live tests.

## Approved Docker image and fail-closed behavior

Provisioning is administrator-controlled and must be reviewed separately:

```powershell
docker build --pull=false --platform linux/amd64 --tag lace-pytest:3.12-v1 docker/pytest
docker image inspect lace-pytest:3.12-v1
docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges `
  --user 65534:65534 lace-pytest:3.12-v1 python -m pytest --version
```

These provisioning commands were documented/unrun during the initial preflight because the Docker Linux engine was unavailable. The image was later provisioned by the administrator. LACE correctly returned an environment error before provisioning instead of running repository tests on the host.

## Troubleshooting

- If `uv` is missing, install it through the project's approved developer workflow or use a clone-local equivalent only with owner approval; do not alter dependency declarations.
- If Docker reports a missing `dockerDesktopLinuxEngine` pipe, start Docker Desktop's Linux engine, verify the approved image locally, then rerun only the marked Docker live tests.
- If the approved image is absent or labels/digest/user controls do not match, treat M4 as blocked; do not pull during an LACE run.
- If workspace applicability fails, preserve the failure evidence and investigate the disposable workspace/Git boundary before attempting M5.
- Do not run arbitrary repository pytest directly on the host.

## Recovery verification

Historical recovery verification: the Windows CRLF applicability issue was fixed in the feature branch. The non-live suite passed `81 passed, 8 deselected`, Ruff format/check passed, and the disposable `validate` and `workspace apply` commands both exited `0` while preserving the original fixture. The restricted `test` command then exited `6` with an environment error because the approved image was absent.

Current M4 verification: the approved image is provisioned; 89 tests were collected, 81 non-Docker tests passed, and all 8 Docker-live tests passed through the approved `DockerExecutor`. Ruff formatting, Ruff linting, and `git diff --check` passed. M4 is locally verified. Do not begin M5 until the owner explicitly approves it.

## Safety reminder

The original repository must remain unchanged until a future, explicit, hash-bound approval/apply workflow exists. A temporary copy is not a security sandbox. Model output, repository files, patches, tests, logs, and commands must remain untrusted.
