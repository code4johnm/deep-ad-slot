# Annex A — Deep Ad Slot Threat Model (STRIDE)

| Field | Value |
| --- | --- |
| Document ID | DAS-SSB-ANNEX-A-001 |
| Parent | DAS-SSB-ARCH-001 |
| Date | 2026-08-24 |
| Method | STRIDE on the 0.1.0 CLI plus target controls |

This annex is a **product-specific** threat model. It is not a penetration-test report and does not include exploit methods, payloads, or classified collection techniques.

## 1. Assets

| Asset | Sensitivity | Why it matters |
| --- | --- | --- |
| GitHub PAT (`GITHUB_TOKEN`) | Tier 4 | Create/update repositories as the operator |
| Operator workstation / venv | High | Runs the TCB and holds `.env` |
| Placement and keyword reports | Tier 1 | Integrity of media-kit advice |
| `parties.json` / auction notes | Tier 2 | Publisher competitive graph |
| `cookie_syncs.json` | Tier 3 | May contain identifier-bearing URLs |
| Auction CSV (`influence`) | Tier 3 | Persona labels, CPMs, tracker flags |
| Analyzed-site trust relationship | — | Permissioned-use; legal/ethical |
| Source, CI, lockfile, SBOM authenticity | High | Supply chain |
| Audit trail of which URL produced a briefing | Moderate | Non-repudiation of a run |

## 2. Adversaries

| Adversary | Access |
| --- | --- |
| Malicious or compromised target page | HTML/script the operator asked to fetch |
| Dependency implant / compromised maintainer | PyPI or git dependency |
| Network attacker on egress path | TLS intercept if validation were disabled (it is not, by httpx default) |
| Malicious insider / careless operator | Local files, PAT, `--push --public` |
| Physical theft of laptop | `.env` and `reports/` |

Out of scope for this increment: nation-state classified collection; browser-exploit development.

## 3. STRIDE

### 3.1 Spoofing

| Scenario | 0.1.0 | Target mitigation |
| --- | --- | --- |
| Page spoofs ad-tech strings to poison scores | Heuristics trust HTML | Document as integrity limit; fixture tests; do not treat scores as exchange truth |
| Typosquat package | Floating `>=` | Hash-pinned lockfile; allowlisted index |
| Spoofed GitHub API | `GITHUB_API` override | `prod` allowlist of API hosts; TLS verify on |

### 3.2 Tampering

| Scenario | 0.1.0 | Target mitigation |
| --- | --- | --- |
| Local `reports/` edited before `--push` | Push reads files from disk | Hash `analysis.json` into briefing README; optional `--push-from-memory` later |
| Lockfile or source tampered in transit | Unsigned clone | Signed tags; `pip` hash checking |
| HTML injection into Markdown report | Domain/title interpolated | Escape or treat as code spans (already mostly fenced); SI-10 tests |

### 3.3 Repudiation

| Scenario | 0.1.0 | Target mitigation |
| --- | --- | --- |
| Unclear which URL/config produced a briefing | Seed URL in REPORT.md (**present**) | Add version, profile, max-pages, analysis hash (FR-DAS-10) |
| Push without local audit | GitHub commit is the only trail | Local minimized audit event before push |

### 3.4 Information disclosure

| Scenario | 0.1.0 | Target mitigation |
| --- | --- | --- |
| Token in logs or GitHub error body | `response.text[:500]` | Redact; never print Authorization |
| Cookie-sync URLs in `cookie_syncs.json` | URL truncated to 240 chars | Redact query values in `prod` |
| `--public` briefing of Tier 3 data | Flag exists | CLI warning; `prod` refuses `--public` unless `allow_public_push` |
| Auction CSV contents on stdout | `influence` prints JSON table | `prod` writes to file under `reports/` instead of full stdout dump (target) |

### 3.5 Denial of service

| Scenario | 0.1.0 | Target mitigation |
| --- | --- | --- |
| Huge HTML | Timeout 20s; text sliced to 20k in snapshot; full HTML kept in memory | Max body bytes; streaming cap |
| `--max-pages` | CLI max 15; implementation fetches `max_pages+1` | Align cap; inter-request delay in `prod` |
| Parser bombs | lxml/BS4 | Size cap; tests with oversized fixtures |

### 3.6 Elevation of privilege

| Scenario | 0.1.0 | Target mitigation |
| --- | --- | --- |
| `--out ../../.ssh` style path | Arbitrary `Path` | Confine to CWD or `reports/` |
| `--repo-name` unexpected characters | Passed to API | Allowlist `[A-Za-z0-9._-]` |
| PAT with broader than `repo` | Documented `repo` only | Operator education; product cannot see unused scopes |
| Command injection via domain slug | `slug_domain` already strips to `[a-z0-9-]` | Keep; tests |

## 4. Residual risk statement (IO)

Cookie-sync URL detection and auction-log `persona` fields can incidentally involve data about persons if the operator’s site or CSV contains it. The product does not resolve those values to U.S. persons and must not grow identity-graph features. Residual risk is accepted for authorized audits and is mitigated by redaction, private default push, and short retention — not by additional collection.

## 5. Mapping to architecture FRs

STRIDE mitigations are implemented through FR-DAS-01…12 in `docs/01-architecture.md` and TEST-* IDs in `conf/profiles.yml` and `docs/03-traceability-seed.csv`.
