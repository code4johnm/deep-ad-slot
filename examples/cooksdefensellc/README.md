# Cooks Defense four-slot package

Approval-safe AdSense markup for the still-thin `cooksdefensellc.com` brochure while publisher `pub-6397321536815225` is in review. Copy these fragments into the site repo. This package does not deploy them.

| File | Where it goes |
| --- | --- |
| `slots.html` | The four blocks in `index.html`, in this order: `#cd-ad-nav`, `#cd-ad-mid`, `#cd-ad-footer`, `#cd-ad-mobile` |
| `index-head.html` | `index.html` `<head>` only. If that loader is already there, keep one copy. |
| `page-ads.js` | Replace the ad block inside the existing `script.js` IIFE |

The three placeholder blocks keep an empty `cd-ad__slot` so the existing stylesheet still reserves the box. The visible text is the "Sponsored" label. Leave the existing `google_ad_section_start(weight=ignore)` wrapper around the hero and `.alert-bar` in place.

## What is live

`#cd-ad-mid` is the only live AdSense unit. It sits after the services section and before values. It is a 300×250 rectangle for client `ca-pub-6397321536815225`.

`#cd-ad-nav`, `#cd-ad-footer`, and `#cd-ad-mobile` are house/sponsor placeholders. Each keeps its wrapper and the visible "Sponsored" label, plus the mobile close control. They do not contain an `adsbygoogle` `<ins>`, and `page-ads.js` does not push them.

Comments in `slots.html` match that split. House/sponsor comments sit only on the three placeholders. The mid-page comment names the single review unit.

## Publisher id and slots

- Publisher id stays `pub-6397321536815225` / `ca-pub-6397321536815225`.
- `ads.txt` stays `google.com, pub-6397321536815225, DIRECT, f08c47fec0942fa0`.
- This repo has no numeric AdSense slot id. Markup omits `data-ad-slot`. Do not invent one.
- Auto ads stay off. Do not add `enable_page_level_ads`.

## Pages and surfaces that stay ad-free

Do not place units on the logo, nav, ticker, hero CTAs, `.alert-bar`, 911 / National Human Trafficking Hotline / text 233733, or the contact form.

Remove the `adsbygoogle.js` loader from `privacy.html`, `terms.html`, `about.html`, and `contact.html`. Do not add an `<ins>` on those pages. The `google-adsense-account` meta is not an ad unit and may stay for site verification. The loader in `index-head.html` belongs on `index.html` only, because that is where `#cd-ad-mid` lives.

Do not add a fifth placement.
