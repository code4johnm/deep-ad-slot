# Deep Ad Slot — `prod` CLI warning and fail-closed expectations

| Field | Value |
| --- | --- |
| Document ID | DAS-SSB-CLI-PROD-001 |
| Relates to | `src/deep_ad_slot/cli.py` (0.1.0) vs target `prod` profile |
| Controls | AC-3, AC-6, PL-4, PT-3, SI-10, SC-7 |
| Test IDs | TEST-ETH-01, TEST-PUSH-01, TEST-PUSH-02, TEST-PATH-01, TEST-AU-01 |

0.1.0 does **not** implement `--profile`. This file is the behavior contract for the implementation increment.

## Invocation (target)

```bash
export DAS_PROFILE=prod
deep-ad-slot --profile prod analyze https://publisher.example
# Token is not required.

deep-ad-slot --profile prod analyze https://publisher.example --push --repo-name ad-intel-publisher
# Requires GITHUB_TOKEN in the environment. Default private. --public is denied.
```

## Stderr warning (emit once per process)

```
Deep Ad Slot prod profile
Use this tool only on sites you own or have permission to audit.
HTML-only fetches under-count JavaScript/consent-gated auctions.
Client identifier-match URLs are a lower bound and may contain
query parameters; prod redacts those values in reports.
Placement scores are relative signals, not live CPMs.
GitHub publish requires --push and a token; default is private.
```

Do not print the token, PAT scopes, or full cookie-sync URLs in this warning.

## Fail-closed table

| Condition | `prod` result | 0.1.0 today |
| --- | --- | --- |
| No `--push` | Local `reports/` only; `GitHubClient` not constructed | Same |
| `--push` without token | Exit non-zero; message without env dump | Same (GitHubError) |
| `--push --public` | Denied | Allowed if flag set |
| `--out` outside CWD/`reports` | Denied | Arbitrary path |
| `--repo-name` not matching `^[A-Za-z0-9._-]+$` | Denied | Passed to API |
| Seed redirects off origin | Stop; do not expand crawl | `follow_redirects=True` |
| RFC1918 / link-local / metadata IP | Denied | Allowed if URL so points |
| `--max-pages` above profile cap | Clamp or deny (cap 5) | CLI max 15; fetches +1 |
| `dump-json` | Omit or redact Tier 3 fields | Full `to_dict()` (HTML already omitted) |
| `influence` | Write under `reports/`; no GitHub | JSON to stdout |
| Debug / verbose HTML dump | Disabled | No such flag (keep it that way in prod) |
| Floating interpreter extra (unpinned sklearn) | Allowed locally; must not be in tagged extra set | Unspecified |

## Exit codes (target)

| Code | Meaning |
| --- | --- |
| 0 | Success |
| 1 | GitHub or ads.txt failure (keep compatibility) |
| 2 | Policy deny (path, profile, public push, private IP) |
| 3 | Fetch policy (redirect / size / timeout) |

## Audit line (target, one line JSON to stderr or `reports/.audit.jsonl`)

```json
{"tool":"deep-ad-slot","version":"0.1.0","profile":"prod","host":"publisher.example","pages":4,"push":false,"exit":0}
```

No token, no query string, no HTML.
