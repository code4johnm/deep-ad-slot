# `.env.example` hardening notes

| Field | Value |
| --- | --- |
| Document ID | DAS-SSB-ENV-001 |
| Relates to | `.env.example` at repository root (0.1.0) |
| Controls | IA-5, SC-28, AC-6, FR-DAS-02 |
| Test ID | TEST-SEC-01 |

## Current file (0.1.0)

```
GITHUB_TOKEN=
GITHUB_OWNER=
GITHUB_API=https://api.github.com
```

`.env` is gitignored (**present**). That is necessary but not sufficient.

## Target `.env.example` (comments only; never real tokens)

```bash
# Deep Ad Slot secrets — copy to .env (gitignored). Never commit values.
# Load only on the operator workstation. The CLI must not read GITHUB_TOKEN
# unless --push is passed (FR-DAS-02 / TEST-PUSH-03).

# Fine-grained or classic PAT. Scope: repo, and only when you will --push.
# Prefer a fine-grained token limited to repositories you allow the tool to create.
# Rotate if it appears in a log or screenshot.
# GITHUB_TOKEN=

# Optional override if whoami should not choose the owner.
# GITHUB_OWNER=

# Default GitHub.com API. Override only for a known GHES base URL (https).
# prod/audit allowlist this host (TEST-FETCH-02 analog for API).
# GITHUB_API=https://api.github.com

# Target CLI profile: dev | audit | prod (not implemented in 0.1.0).
# DAS_PROFILE=prod
```

## Rules

1. Do not put example tokens (`ghp_your_token` in README is a documentation smell; prefer `ghp_` + redacted form or `YOUR_TOKEN` without a plausible body).
2. `python-dotenv` `load_dotenv()` is global in `cli.py` today. Target: load for push path only, or load but refuse to construct `GitHubClient` without `--push`.
3. Secret scan CI must ignore `.env.example` placeholders and fail on `.env` or `ghp_` in other paths.
4. Runtime: token in process environment is visible to the same OS user; this baseline does not claim otherwise. Workstation full-disk encryption is an operator control (MP-family, out of product TCB).
5. `GITHUB_API` in `prod` must be HTTPS. HTTP is fail-closed.

## README sample commands

Keep `export GITHUB_TOKEN=...` in the operator runbook, not a real PAT. The existing README uses `ghp_your_token` — replace with a clearly fake sentinel in a later docs edit (`CHANGE_ME_DO_NOT_COMMIT`).
