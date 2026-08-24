from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Org:
    name: str
    role: str
    domains: tuple[str, ...]


# Organizational map used to collapse domains into bidders / trackers / measurement.
ORGS: tuple[Org, ...] = (
    Org("Alphabet", "platform", ("google.com", "googleapis.com", "doubleclick.net", "googlesyndication.com", "googleadservices.com", "googletagmanager.com", "googletagservices.com", "2mdn.net", "adsense.com")),
    Org("Meta", "platform", ("facebook.com", "facebook.net", "fbcdn.net", "instagram.com")),
    Org("Amazon", "exchange", ("amazon-adsystem.com", "amazon.com")),
    Org("Adobe", "dmp", ("demdex.net", "omtrdc.net", "adobe.com", "adobetm.com")),
    Org("Microsoft / Xandr", "dsp", ("adnxs.com", "appnexus.com", "xandr.com", "bing.com")),
    Org("Index Exchange", "ssp", ("indexww.com", "casalemedia.com", "indexexchange.com")),
    Org("Magnite", "ssp", ("rubiconproject.com", "magnite.com")),
    Org("OpenX", "ssp", ("openx.net", "openx.com")),
    Org("PubMatic", "ssp", ("pubmatic.com")),
    Org("Criteo", "dsp", ("criteo.com", "criteo.net")),
    Org("The Trade Desk", "dsp", ("adsrvr.org", "thetradedesk.com")),
    Org("Verizon / Yahoo", "platform", ("yahoo.com", "aol.com", "advertising.com", "adtechus.com")),
    Org("LiveRamp", "identity", ("rlcdn.com", "liveramp.com", "id5-sync.com")),
    Org("DoubleVerify", "measurement", ("doubleverify.com", "dv.tech")),
    Org("Integral Ad Science", "measurement", ("adsafeprotected.com", "integralads.com")),
    Org("Comscore", "measurement", ("scorecardresearch.com", "comscore.com")),
    Org("Quantcast", "dmp", ("quantserve.com", "quantcast.com")),
    Org("Lotame", "dmp", ("crwdcntrl.net", "lotame.com")),
    Org("Oracle", "dmp", ("bluekai.com", "bkrtx.com", "addthis.com")),
    Org("Taboola", "native", ("taboola.com")),
    Org("Outbrain", "native", ("outbrain.com")),
    Org("ID5", "identity", ("id5-sync.com", "id5.io")),
    Org("Prebid", "wrapper", ("prebid.org", "prebid.js")),
)


def org_for_host(host: str) -> Org | None:
    host = host.lower().lstrip(".")
    if host.startswith("www."):
        host = host[4:]
    for org in ORGS:
        for domain in org.domains:
            if host == domain or host.endswith("." + domain) or domain in host:
                return org
    return None


def classify_script_url(url: str) -> tuple[str, str] | None:
    from urllib.parse import urlparse

    host = urlparse(url).netloc.lower()
    org = org_for_host(host)
    if not org:
        return None
    return org.name, org.role
