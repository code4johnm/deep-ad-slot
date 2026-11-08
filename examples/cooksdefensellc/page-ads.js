  /* Single review unit (#cd-ad-mid). Replace the ad block inside the existing script.js IIFE.
     House placeholders #cd-ad-nav, #cd-ad-footer, and #cd-ad-mobile have no ins and must not be pushed.
     Do not add enable_page_level_ads. Auto ads stay off. */
  const requestPageAds = () => {
    const nodes = document.querySelectorAll('#cd-ad-mid ins.adsbygoogle');
    if (nodes.length !== 1) return false;
    if (![...nodes].every((ins) => ins.offsetWidth >= 50 && ins.offsetHeight >= 40)) return false;
    nodes.forEach(() => {
      try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch (e) { /* no fill */ }
    });
    return true;
  };
  const schedulePageAds = (left) => {
    if (requestPageAds() || left <= 0) return;
    requestAnimationFrame(() => schedulePageAds(left - 1));
  };
  if (document.readyState === 'complete') schedulePageAds(12);
  else window.addEventListener('load', () => schedulePageAds(12), { once: true });

  const adBar = document.getElementById('cd-ad-mobile');
  const adClose = document.getElementById('cd-ad-mobile-close');
  if (adBar && adClose) {
    const setSafe = (on) => {
      adBar.classList.toggle('is-safe', on);
      document.documentElement.classList.toggle('cd-ad-anchor-on', on);
    };
    adClose.addEventListener('click', () => {
      adBar.hidden = true;
      setSafe(false);
    });
    const guarded = document.querySelectorAll('.hero-actions, .alert-bar, .contact-form');
    const updateAdAnchor = () => {
      if (adBar.hidden || window.innerWidth > 767) {
        setSafe(false);
        return;
      }
      const band = 64;
      const hit = Array.from(guarded).some((el) => {
        const r = el.getBoundingClientRect();
        return r.bottom > window.innerHeight - band && r.top < window.innerHeight;
      });
      setSafe(!hit);
    };
    updateAdAnchor();
    window.addEventListener('scroll', updateAdAnchor, { passive: true });
    window.addEventListener('resize', updateAdAnchor);
  }
