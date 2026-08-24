<p align="center">
  <img src="assets/logo.png" alt="Deep Ad Slot" width="168">
</p>

# Deep Ad Slot

Give the app a website. It inspects page structure, scores the highest-value ad placements, extracts keywords, maps demand and tracker parties, and can push a briefing into a new GitHub repository.

This is a publisher / media-kit helper, not a CPM guarantee. Placement scores combine layout signals with current inventory practice: viewability, above-the-fold leaderboards, in-content after paragraph 2, sticky sidebar, and mobile sticky footer.

## What it does

1. Fetches the URL and a few same-domain pages.
2. Detects layout landmarks (header, nav, article, sidebar, footer).
3. Detects ad tech (AdSense, GPT, Prebid, Amazon APS, Taboola, measurement tags).
4. Maps demand and tracker organizations on the page.
5. Flags client identifier-match URLs. Treats those as a lower bound — partners that never touch the browser are invisible here.
6. Ranks recommended slots with formats and implementation notes.
7. Extracts keywords and commercial variants.
8. Optionally creates a GitHub repo and pushes the briefing.
9. Optionally ranks which tracker flags move bidder CPMs from a collected auction log.

## Quick start

```bash
git clone https://github.com/code4johnm/deep-ad-slot.git
cd deep-ad-slot
python -m venv .venv
source .venv/bin/activate
pip install -e .

deep-ad-slot analyze https://example.com
```

Write reports to a folder:

```bash
deep-ad-slot analyze https://example.com --out ./reports/example
```

Create a GitHub repo and push the briefing (needs `GITHUB_TOKEN`):

```bash
export GITHUB_TOKEN=ghp_your_token
deep-ad-slot analyze https://example.com --push --repo-name ad-intel-example --private
```

## Auction log → tracker influence

Collect bids from a client wrapper (`pbjs.getBidResponses()` or equivalent) into a CSV:

```
bidder,cpm,persona,site,tracker_alphabet,tracker_meta,tracker_doubleverify
```

`tracker_*` columns are 0/1 flags for whether that organization was allowed to see the session before the auction.

```bash
deep-ad-slot influence examples/bids.sample.csv
```

The command reports, per bidder:

- mean CPM delta when a tracker flag is on vs off
- optional random-forest feature ranks if `scikit-learn` is installed

Interpretation: a tracker that consistently moves a bidder's band (low / mid / high CPM) is treated as a data-sharing edge, whether that edge is in the browser or behind the auction.

Install the optional model extra:

```bash
pip install scikit-learn
```

## ads.txt

```bash
deep-ad-slot ads-txt https://example.com
```

## GitHub access

Create a PAT with `repo` scope. Put it in the environment or `.env`:

```
GITHUB_TOKEN=ghp_...
GITHUB_OWNER=code4johnm
```

## CLI

```
deep-ad-slot analyze URL
  --out PATH
  --max-pages N
  --push
  --owner NAME
  --repo-name NAME
  --private / --public
  --create-repo / --no-create-repo
  --branch NAME

deep-ad-slot influence BIDS.csv
deep-ad-slot ads-txt URL
deep-ad-slot dump-json URL
```

## Output

```
reports/<domain>/
  REPORT.md
  analysis.json
  placements.json
  keywords.csv
  parties.json
  cookie_syncs.json
```

## Notes

- Use this on sites you own or have permission to audit.
- Some sites hide auctions and ads behind consent / JavaScript. HTML-only fetches then show layout slots plus whatever scripts are inline.
- Client identifier matching under-counts server-side partners. Use an auction log plus tracker on/off flags when you need those edges.
- Keyword values and placement scores are relative, not live exchange prices.
- Branding: `assets/logo.png` (mark), `assets/icon.png` (app icon), `assets/social-preview.png` (1280×640). Set the social image in GitHub → Settings → General → Social preview.
