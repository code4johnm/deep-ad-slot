# AdSlot Scout

Give the app a website. It inspects page structure, scores the highest-value ad placements, extracts keywords, and can push a full briefing into a new GitHub repository.

This is a **publisher / media-kit helper**, not a CPM guarantee. Scores combine layout signals with current placement research: viewability, above-the-fold leaderboards, in-content after paragraph 2, sticky sidebar, and mobile sticky footer. Real yield still depends on traffic quality, geography, vertical, and demand partners.

## What it does

1. Fetches the URL and a few same-domain pages.
2. Detects layout landmarks (header, nav, article, sidebar, footer).
3. Detects existing ad tech (AdSense, GPT, Prebid, Taboola, and others).
4. Ranks recommended slots with formats, viewability notes, and implementation hints.
5. Extracts keywords from titles, headings, meta, and body copy, then expands commercial variants.
6. Writes a Markdown briefing + JSON payload.
7. Optionally creates a new GitHub repo and pushes those artifacts.

## Quick start

```bash
git clone https://github.com/code4johnm/adslot-scout.git
cd adslot-scout
python -m venv .venv
source .venv/bin/activate
pip install -e .

adslot-scout analyze https://example.com
```

Write reports to a folder:

```bash
adslot-scout analyze https://example.com --out ./reports/example
```

Create a GitHub repo and push the briefing (needs `GITHUB_TOKEN`):

```bash
export GITHUB_TOKEN=ghp_your_token
adslot-scout analyze https://example.com --push --repo-name ad-intel-example --private
```

Push into an existing repo instead of creating one:

```bash
adslot-scout analyze https://example.com --push --owner code4johnm --repo-name existing-repo --no-create-repo
```

## GitHub access

The app talks to the GitHub REST API. Create a classic or fine-grained personal access token with:

- `repo` scope (create private repos + commit files)

Fine-grained alternative:

- Contents: write
- Administration: write only if you want the tool to create new repositories

Put the token in the environment or a `.env` file:

```
GITHUB_TOKEN=ghp_...
GITHUB_OWNER=code4johnm
```

`--owner` defaults to the authenticated user when omitted.

## CLI

```
adslot-scout analyze URL [OPTIONS]

  --out PATH              Local output directory
  --max-pages N           Extra same-domain pages to crawl (default 4)
  --push                  Create/update a GitHub repo with the report
  --owner NAME            GitHub owner or org
  --repo-name NAME        Repo name (default ad-intel-<domain>)
  --private / --public    New repo visibility (default private)
  --create-repo / --no-create-repo
  --branch NAME           Branch to commit to (default main)
```

## Output

```
reports/<domain>/
  REPORT.md          Human briefing
  analysis.json      Machine-readable result
  keywords.csv       Keyword list for ads / SEO
  placements.json    Ranked slots only
```

When `--push` is used, the same files land in the remote repo under `briefing/`.

## Notes

- Use this on sites you own or have permission to audit. Respect robots.txt and terms of service.
- Some sites block generic user agents or load ads only after consent / JavaScript. In those cases the tool still recommends slots from layout.
- Keyword values are relative commercial-intent scores, not live Google Ads CPCs.
