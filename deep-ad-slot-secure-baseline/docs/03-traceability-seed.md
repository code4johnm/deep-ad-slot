# Deep Ad Slot — Compliance Traceability Seed

| Field | Value |
| --- | --- |
| Document ID | DAS-SSB-TRC-001 |
| Baseline | DAS-SSB-2026-001 v1.0.0-increment-1 |
| Date | 2026-08-24 |
| Machine-readable companion | `deep-ad-slot-secure-baseline/docs/03-traceability-seed.csv` |

This seed maps **features** to NIST SP 800-53 Rev. 5, SSDF (SP 800-218 v1.1), CISA/SBOM, and IO/privacy notes. It is expandable later to control-enhancement and additional test-ID granularity. It is **not** a complete 800-53 implementation statement and **not** an ATO overlay.

Legend for **State**: `present` = in product 0.1.0; `partial`; `target`; `N/A`.

| Feature ID | Feature | FR | 800-53 (primary) | SSDF | CISA / SBOM | IO / privacy | State | Test ID |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F-01 | Pinned dependencies on release tags | FR-DAS-08 | SR-3, CM-2 | PW.4, PS.3 | Transitive SBOM completeness | — | target | TEST-SBOM-01 |
| F-02 | Secrets never in git; `.env` gitignored | FR-DAS-02 | IA-5, SC-28 | PS.1 | — | Token is not USP; still high-value credential | present | TEST-SEC-01 |
| F-03 | Fetch timeouts; same-domain bound | FR-DAS-03 | SC-7, SC-5 | PW.5 | — | Limits accidental off-origin collection | partial | TEST-FETCH-01 |
| F-04 | Fetch size limits, private-IP deny, rate limit | FR-DAS-04 | SC-5, SC-7 | PW.5 | — | Reduces incidental crawl of internal hosts | target | TEST-FETCH-02 |
| F-05 | `--out` / `--repo-name` sanitization | FR-DAS-05 | SI-10, AC-6 | PW.5 | — | — | target | TEST-PATH-01 |
| F-06 | HTML omitted from `analysis.json` | FR-DAS-06 | PT-3, SI-12 | PW.9 | — | Minimizes page-body retention | present | TEST-MIN-01 |
| F-07 | Cookie-sync query redaction in `prod` | FR-DAS-06 | PT-2, PT-3 | PW.9 | — | Residual USP risk if not redacted | partial | TEST-MIN-02 |
| F-08 | Auction CSV not pushed to GitHub | FR-DAS-07 | AC-3, PT-2 | PW.9 | — | Persona labels stay local | present (no push path) | TEST-BID-01 |
| F-09 | `--push` opt-in; default private | FR-DAS-01, FR-DAS-12 | AC-3, AC-6 | PW.1 | — | Default deny remote copy | present | TEST-PUSH-01 |
| F-10 | PAT loaded only for push | FR-DAS-02 | AC-6, IA-5 | PS.1 | — | — | partial (client constructed only in push branch) | TEST-PUSH-03 |
| F-11 | SPDX 3.x SBOM + VEX with release | FR-DAS-08 | SR-4, SI-7, RA-5 | PS.3, RV.1 | CISA 2026 minimum elements | — | target | TEST-SBOM-01 |
| F-12 | Signed git tags / optional wheel attestations | FR-DAS-08 | SI-7, CM-14 | PS.2 | Author-signed SBOM | — | target | TEST-SIGN-01 |
| F-13 | Minimized audit / no token in logs | FR-DAS-10 | AU-2, AU-3 | RV.1 | — | Logs are not a person-collection channel | target | TEST-AU-01 |
| F-14 | Permissioned-use policy + CLI warning | FR-DAS-09 | PL-4, SA-8 | PO.1 | Secure by Design (safe defaults) | Purpose limitation | partial (README only) | TEST-ETH-01 |
| F-15 | Identifying User-Agent | — | SA-8 | PO.5 | Transparency | Good-neighbor; not covert | present | TEST-UA-01 |
| F-16 | Optional sklearn ephemeral fit | FR-DAS-11 | SA-8 | PW.1 | SBOM-for-AI N/A | No identity model | present | TEST-ML-01 |
| F-17 | Secret / SAST / license scan in CI | FR-DAS-08 | SA-11, RA-5, CM-7 | PW.7, PW.8 | License on each component | — | target | TEST-CI-01 |
| F-18 | Third-party intake record | FR-DAS-08 | SR-1, SR-3, SR-11 | PO.3 | C-SCRM | — | target | TEST-SCRM-01 |
| F-19 | Profile contract `dev`/`audit`/`prod` | NFR-DAS-05 | CM-2, CM-6 | PW.1 | — | `prod` tightens Tier 3 handling | target | TEST-PROF-01 |
| F-20 | Briefing provenance (version, hash) | FR-DAS-10 | AU-10, SI-7 | PS.2 | SBOM stored with artifact | — | partial (seed URL only) | TEST-AU-02 |

## Non-applicable rows (explicit)

| Item | Rationale |
| --- | --- |
| IEC 62443, ISO 26262, ISO 13485 / IEC 62304 | Not OT, automotive, or medical software |
| NIST SP 800-204 | Not a microservice in 0.1.0 |
| NIST SP 800-218A / CISA SBOM-for-AI | No generative or foundation model artifact |
| CNSSI 1253 | Only if a program categorizes a hosted deployment as NSS |
| STIG certification | Benchmarks only; no certification claimed |
| Inbound TLS server hardening | CLI has no inbound listeners |

## Expansion rules (later increment)

Add columns: control enhancement (e.g. AC-6(1)), assessment procedure, evidence path under `evidence/<version>/`, and implementation PR. Do not drop N/A rows; mark them N/A with rationale.
