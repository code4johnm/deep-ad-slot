# Deep Ad Slot — Secure Software Engineering Baseline

| Field | Value |
| --- | --- |
| Product | Deep Ad Slot (`deep-ad-slot` / Python package `deep_ad_slot`) |
| Repository | https://github.com/code4johnm/deep-ad-slot |
| Baseline ID | DAS-SSB-2026-001 |
| Baseline version | 1.0.0-increment-1 |
| Product version in scope | 0.1.0 |
| Date | 2026-08-24 |
| License of product | MIT |
| Publisher of this package | Quantum Research Laboratories LLC (engineering documentation) |
| Package root | `deep-ad-slot-secure-baseline/` |

This package is an **auditable engineering baseline** for Deep Ad Slot, a local-first Python CLI that produces publisher / media-kit briefings from HTML-only site inspection and optional auction-log analysis. It is written against the live module layout (`fetch` → analysis → `report` → optional `github_push`) and is intended to be adopted as in-repo documentation and configuration, not as a separate product.

**Honesty rule.** Controls labeled **present** exist in product 0.1.0. Controls labeled **target** are the engineering contract of this baseline. This increment does **not** implement runtime code changes; it specifies them.

## Authority limits

This work is **not** an official U.S. Government issuance. It does **not** grant or imply Authorization to Operate (ATO). It does **not** create collection authorities under Executive Order 12333. It does **not** publish key material, exploit methods, or classified configurations. Authors of this baseline are not authorizing officials, intelligence officers, or catalog publishers.

NIST SP 800-37 Rev. 2 is used for **process alignment only**. DoDI 8510.01 applies only when a U.S. Government acquirer places Deep Ad Slot in a Department of Defense (DoD) information system. CNSSI 1253 overlays apply only if the deploying program categorizes a hosted deployment as a National Security System (NSS). SRGs/STIGs are cited only as technical benchmarks; this product is **not** claimed “STIG certified.” The statutory name **Department of Defense (DoD)** is used.

This baseline does **not** design consent-wall bypass, unauthorized scraping, tracker-graph weaponization, or exfiltration of third-party data outside an authorized audit.

## Increment 1 contents

| Path | Content |
| --- | --- |
| `deep-ad-slot-secure-baseline/docs/01-architecture.md` | Requirements analysis and high-level architecture |
| `deep-ad-slot-secure-baseline/docs/02-project-structure.md` | Repository deltas, ownership, CI/CD, C-SCRM |
| `deep-ad-slot-secure-baseline/docs/03-traceability-seed.md` | Human-readable feature → control seed |
| `deep-ad-slot-secure-baseline/docs/03-traceability-seed.csv` | Expandable machine-readable matrix |
| `deep-ad-slot-secure-baseline/docs/annex-a-threat-model.md` | Product-specific STRIDE annex |
| `deep-ad-slot-secure-baseline/conf/profiles.yml` | `dev` / `audit` / `prod` profile contract |
| `deep-ad-slot-secure-baseline/conf/sbom-policy.yml` | CISA 2026 SBOM minimum-elements policy |
| `deep-ad-slot-secure-baseline/examples/github-actions-release.yml.example` | Test + SBOM + signed-tag pipeline |
| `deep-ad-slot-secure-baseline/examples/third-party-intake.record.example` | C-SCRM intake record |
| `deep-ad-slot-secure-baseline/examples/env-hardening.md` | `.env.example` hardening notes |
| `deep-ad-slot-secure-baseline/examples/cli-prod-behavior.md` | `prod` CLI warning and fail-closed expectations |

## Later increments (not in this package)

Hardening and secure-coding guide for Python HTTP + HTML parsing; build and release procedures; runtime operations guide; testing and validation plan; SBOM process with worked examples; maintenance and deployment; full control-enhancement and test-ID matrix; ATO package artifacts (SSP, SAP, POA&M, eMASS import).
