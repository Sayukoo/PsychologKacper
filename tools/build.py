#!/usr/bin/env python3
"""Generator podstron treściowych psychologkacper.pl.

Uruchomienie (z katalogu głównego repozytorium):

    python tools/build.py

Czyta fragmenty z tools/content/*.html (nagłówek <!--META {json} --> + treść HTML)
i zapisuje gotowe strony w katalogu głównym oraz w poradnik/. Przy okazji
odświeża sitemap.xml, llms.txt i hub poradnika. Bez zależności zewnętrznych.

Strony pisane ręcznie (index, testy, kontakt, materialy) nie są nadpisywane —
ich nawigację i stopkę utrzymuje się osobno.
"""
from __future__ import annotations

import html
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = Path(__file__).resolve().parent / "content"
SITE = "https://psychologkacper.pl"

# --- Fakty o praktyce: jedno źródło prawdy dla szablonu, llms.txt i schemy ---
PHONE_DISPLAY = "572 450 606"
PHONE_TEL = "+48572450606"
EMAIL = "kackul17@gmail.com"
CALENDLY = "https://calendly.com/kacperkulesza/15min"
LINKEDIN = "https://www.linkedin.com/in/konstruktywizm/"
TIKTOK = "https://www.tiktok.com/@psycholog.kacper"
PRICE_SESSION = "150"
PERSON_ID = f"{SITE}/#kacper"
ORG_ID = f"{SITE}/#psychologist"
WEBSITE_ID = f"{SITE}/#website"

MONTHS = ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca",
          "sierpnia", "września", "października", "listopada", "grudnia"]

# Strony pisane ręcznie — trafiają do sitemap.xml i llms.txt.
STATIC_PAGES = [
    {"url": "", "title": "Strona główna", "desc": "Oferta, cennik, FAQ i rezerwacja bezpłatnej 15-minutowej rozmowy wstępnej."},
    {"url": "testy.html", "title": "Testy psychologiczne online", "desc": "Cztery bezpłatne kwestionariusze samooceny: ASRS (ADHD), GAD-7 (lęk), PHQ-9 (depresja), WHO-5 (dobrostan). Wynik od razu, nic nie jest zapisywane."},
    {"url": "materialy.html", "title": "Darmowe materiały i narzędzia", "desc": "Karty pracy, ćwiczenia i schematy psychologiczne."},
    {"url": "kontakt.html", "title": "Kontakt", "desc": "Telefon, e-mail i formularz kontaktowy."},
]

SECTIONS = {
    "service": {"label": "Oferta", "crumb": None},
    "problem": {"label": "W czym pomagam", "crumb": ("W czym pomagam", "index.html#w-czym-pomagam")},
    "test": {"label": "Testy psychologiczne", "crumb": ("Testy psychologiczne", "testy.html")},
    "article": {"label": "Poradnik", "crumb": ("Poradnik", "poradnik/")},
}

ARROW = ('<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" '
         'stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13"></path><path d="M13 6l6 6-6 6"></path></svg>')
ARROW_WHITE = ARROW.replace('stroke="currentColor"', 'stroke="#FFFFFF"')
CHEVRON = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
           'stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"></path></svg>')
PLUS = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.6" '
        'stroke-linecap="round"><path d="M12 5v14"></path><path d="M5 12h14"></path></svg>')
PHONE_SVG = ('<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
             'stroke-linejoin="round"><path d="M6 3.5h3l1.5 4-2 1.5a11 11 0 0 0 5.5 5.5l1.5-2 4 1.5v3c0 1.1-.9 2-2 2A15.5 15.5 0 0 1 4 5.5c0-1.1.9-2 2-2Z"></path></svg>')
TIKTOK_SVG = ('<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
              'stroke-linejoin="round"><path d="M14.5 3.5v11a4 4 0 1 1-4-4"></path><path d="M14.5 3.5c.4 2.7 2.2 4.4 5 4.7"></path></svg>')
MAIL_SVG = ('<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round"><rect x="3" y="5.5" width="18" height="13" rx="2.5"></rect><path d="m4 7 8 6 8-6"></path></svg>')


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def strip_tags(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", text))).strip()


def pl_date(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def load_pages() -> list[dict]:
    pages = []
    for path in sorted(CONTENT.glob("*.html")):
        raw = path.read_text(encoding="utf-8")
        match = re.match(r"\s*<!--META\s*(\{.*?\})\s*-->\s*(.*)", raw, re.S)
        if not match:
            sys.exit(f"Brak nagłówka <!--META {{...}} --> w {path.name}")
        meta = json.loads(match.group(1))
        meta["body"] = match.group(2).strip()
        meta["source"] = path.name
        for key in ("slug", "type", "title", "description", "h1", "lead", "card", "updated"):
            if key not in meta:
                sys.exit(f"{path.name}: brak pola „{key}”")
        if meta["type"] not in SECTIONS:
            sys.exit(f"{path.name}: nieznany typ „{meta['type']}”")
        meta.setdefault("published", meta["updated"])
        meta.setdefault("order", 50)
        pages.append(meta)
    pages.sort(key=lambda p: (p["order"], p["slug"]))
    return pages


def depth_prefix(slug: str) -> str:
    return "../" * slug.count("/")


_REL_LINK = re.compile(r'(href|src)="(?!https?:|mailto:|tel:|#|/|\.\./)([^"]+)"')


def localize(fragment: str, r: str) -> str:
    """Treści piszemy z linkami względem katalogu głównego; tu dostają prefiks dla podkatalogów."""
    return _REL_LINK.sub(lambda m: f'{m.group(1)}="{r}{m.group(2)}"', fragment) if r else fragment


def by_type(pages: list[dict], kind: str) -> list[dict]:
    return [p for p in pages if p["type"] == kind]


# --------------------------------------------------------------------------
# Wspólne fragmenty: nagłówek, stopka
# --------------------------------------------------------------------------

def nav_items(r: str) -> list[tuple[str, str, str]]:
    """(etykieta desktop, etykieta mobile, href)"""
    return [
        ("O mnie", "O mnie", f"{r}index.html#o-mnie"),
        ("W czym pomagam", "W czym pomagam", f"{r}index.html#w-czym-pomagam"),
        ("Cennik", "Cennik", f"{r}index.html#cennik"),
        ("Testy", "Testy psychologiczne", f"{r}testy.html"),
        ("Poradnik", "Poradnik", f"{r}poradnik/"),
        ("Materiały", "Darmowe materiały", f"{r}materialy.html"),
        ("Kontakt", "Kontakt", f"{r}kontakt.html"),
    ]


def header_html(r: str, active: str) -> str:
    desktop = "\n".join(
        f'        <a href="{href}" class="nav-link{" active" if label == active else ""}">{label}</a>'
        for label, _, href in nav_items(r)
    )
    mobile_links = [("Strona główna", "Strona główna", f"{r}index.html")] + nav_items(r)
    mobile_links.insert(-1, ("FAQ", "Częste pytania (FAQ)", f"{r}index.html#faq"))
    mobile = "\n".join(
        f'      <a href="{href}" class="mobile-nav-link{" active" if label == active else ""}">\n'
        f'        <span>{mlabel}</span>\n        {CHEVRON}\n      </a>'
        for label, mlabel, href in mobile_links
    )
    return f"""  <a href="#main-content" class="skip-link">Przejdź do treści</a>
  <div class="scroll-progress" aria-hidden="true"><div class="scroll-progress__bar"></div></div>

  <header class="site-header">
    <div class="nav-shell">
      <a href="{r}index.html" class="brand-link">
        <span class="brand-logo">KK</span>
        <span class="brand-text">Kacper Kulesza <span class="dot">·</span> psycholog</span>
      </a>
      <nav class="nav-links" aria-label="Główna nawigacja">
{desktop}
      </nav>
      <a href="{r}index.html#kontakt" class="btn-cta desktop-nav-cta">
        Konsultacja 15 min
        {ARROW_WHITE}
      </a>
      <button id="mobile-menu-btn" class="mobile-menu-btn" aria-label="Otwórz menu" aria-expanded="false">
        <span class="hamburger-line"></span>
        <span class="hamburger-line"></span>
        <span class="hamburger-line"></span>
      </button>
    </div>
  </header>

  <div id="mobile-backdrop" class="mobile-backdrop"></div>

  <div id="mobile-drawer" class="mobile-drawer">
    <div class="mobile-drawer-header">
      <div class="brand-link">
        <span class="brand-logo">KK</span>
        <span class="brand-text">Kacper Kulesza <span class="dot">·</span> psycholog</span>
      </div>
      <button id="mobile-drawer-close" class="mobile-drawer-close" aria-label="Zamknij menu">✕</button>
    </div>

    <nav class="mobile-nav-links" aria-label="Nawigacja mobilna">
{mobile}
    </nav>

    <a href="{r}index.html#kontakt" class="btn-cta" style="margin-top: 24px; padding: 14px 20px; font-size: 1rem; justify-content: center; width: 100%; text-align: center; box-sizing: border-box;">
      Zarezerwuj konsultację 15 min
      {ARROW_WHITE}
    </a>

    <div class="mobile-drawer-contact">
      <a href="tel:{PHONE_TEL}" class="mobile-contact-pill">{PHONE_SVG.replace('currentColor', '#1C86EE')} {PHONE_DISPLAY}</a>
      <a href="mailto:{EMAIL}" class="mobile-contact-pill">{MAIL_SVG.replace('currentColor', '#1C86EE')} {EMAIL}</a>
    </div>
  </div>
"""


def foot_sitemap_html(pages: list[dict], r: str) -> str:
    def col(title: str, links: list[tuple[str, str]]) -> str:
        items = "\n".join(f'            <li><a href="{href}">{esc(label)}</a></li>' for label, href in links)
        return f"        <div>\n          <h3>{title}</h3>\n          <ul>\n{items}\n          </ul>\n        </div>"

    service = [(p["card"], f'{r}{p["slug"]}') for p in by_type(pages, "service")]
    service += [("Cennik", f"{r}index.html#cennik"), ("Umów bezpłatne 15 minut", f"{r}index.html#kontakt"), ("Kontakt", f"{r}kontakt.html")]
    problems = [(p["card"], f'{r}{p["slug"]}') for p in by_type(pages, "problem")]
    tests = [("Wszystkie testy", f"{r}testy.html")] + [(p["card"], f'{r}{p["slug"]}') for p in by_type(pages, "test")]
    articles = [(p["card"], f'{r}{p["slug"]}') for p in by_type(pages, "article")]
    articles.append(("Wszystkie artykuły", f"{r}poradnik/"))
    return (
        '      <!-- foot-sitemap:start (generowane przez tools/build.py) -->\n'
        '      <nav class="foot-sitemap" aria-label="Mapa strony">\n'
        + "\n".join([col("Konsultacje", service), col("W czym pomagam", problems), col("Testy", tests), col("Poradnik", articles)])
        + "\n      </nav>\n      <!-- foot-sitemap:end -->"
    )


def footer_html(pages: list[dict], r: str) -> str:
    return f"""  <footer class="site-footer">
    <div class="container">
{foot_sitemap_html(pages, r)}
      <div class="foot-grid">
        <span class="brand-logo" style="font-size: 2rem;">KK</span>
        <div style="display: flex; flex-direction: column; gap: 12px;">
          <span style="font-size: 0.98rem; font-weight: 700; color: var(--color-text-main);">Kacper Kulesza – psycholog · konsultacje online</span>
          <div class="foot-contact-links">
            <a href="tel:{PHONE_TEL}" class="foot-contact-item">{PHONE_SVG} {PHONE_DISPLAY}</a>
            <a href="mailto:{EMAIL}" class="foot-contact-item">{MAIL_SVG} {EMAIL}</a>
            <a href="{TIKTOK}" class="foot-contact-item" target="_blank" rel="me noopener">{TIKTOK_SVG} TikTok</a>
          </div>
        </div>
        <div style="text-align: right; font-size: 0.8125rem; line-height: 1.6; color: var(--color-text-muted);">
          © 2026 Kacper Kulesza<br><a href="{r}index.html#privacy-toggle-btn">Polityka prywatności</a>
        </div>
      </div>
    </div>
  </footer>

  <button class="back-to-top" type="button" aria-label="Wróć na górę strony">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5"></path><path d="M5 12l7-7 7 7"></path></svg>
  </button>

  <script src="{r}js/main.js"></script>
"""


def head_html(*, title: str, description: str, canonical: str, r: str, og_type: str, graph: list[dict],
              extra_meta: str = "") -> str:
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)
    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{canonical}">
  <meta name="author" content="Kacper Kulesza">
{extra_meta}
  <link rel="icon" type="image/svg+xml" href="{r}favicon.svg">
  <link rel="apple-touch-icon" href="{r}favicon.svg">
  <meta name="theme-color" content="#1C86EE">

  <meta property="og:type" content="{og_type}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:site_name" content="Kacper Kulesza – Psycholog">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:image" content="{SITE}/images/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:locale" content="pl_PL">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{SITE}/images/og-image.png">

  <script type="application/ld+json">
{ld}
  </script>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,600&display=swap">
  <link rel="stylesheet" href="{r}css/style.css?v=4.0">
</head>
"""


# --------------------------------------------------------------------------
# Schema.org
# --------------------------------------------------------------------------

def person_ref() -> dict:
    return {"@type": "Person", "@id": PERSON_ID, "name": "Kacper Kulesza", "jobTitle": "Psycholog", "url": f"{SITE}/"}


def org_ref() -> dict:
    return {"@type": "ProfessionalService", "@id": ORG_ID, "name": "Kacper Kulesza – Psycholog", "url": f"{SITE}/"}


def breadcrumb_ld(trail: list[tuple[str, str]]) -> dict:
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": name, "item": url}
            for i, (name, url) in enumerate(trail, start=1)
        ],
    }


def faq_ld(url: str, faq: list[list[str]]) -> dict:
    return {
        "@type": "FAQPage",
        "@id": f"{url}#faq",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
            for q, a in faq
        ],
    }


def page_graph(page: dict, url: str, trail: list[tuple[str, str]]) -> list[dict]:
    webpage = {
        "@type": "WebPage",
        "@id": url,
        "url": url,
        "name": page["title"],
        "description": page["description"],
        "inLanguage": "pl-PL",
        "isPartOf": {"@type": "WebSite", "@id": WEBSITE_ID},
        "datePublished": page["published"],
        "dateModified": page["updated"],
        "author": person_ref(),
    }
    graph: list[dict] = [webpage, breadcrumb_ld(trail)]
    kind = page["type"]
    if kind == "service":
        graph.append({
            "@type": "Service",
            "@id": f"{url}#service",
            "name": page["h1"],
            "serviceType": "Konsultacja psychologiczna online",
            "description": strip_tags(page["lead"]),
            "url": url,
            "provider": org_ref(),
            "areaServed": {"@type": "Country", "name": "Polska"},
            "availableChannel": {"@type": "ServiceChannel", "serviceUrl": CALENDLY, "name": "Wideorozmowa online"},
            "offers": [
                {"@type": "Offer", "name": "Rozmowa wstępna (15 minut)", "price": "0", "priceCurrency": "PLN"},
                {"@type": "Offer", "name": "Konsultacja psychologiczna (60 minut)", "price": PRICE_SESSION, "priceCurrency": "PLN"},
            ],
        })
    elif kind == "problem":
        graph.append({
            "@type": "Service",
            "@id": f"{url}#service",
            "name": f'Konsultacja psychologiczna online: {page["card"].lower()}',
            "serviceType": "Konsultacja psychologiczna online",
            "description": strip_tags(page["lead"]),
            "url": url,
            "provider": org_ref(),
            "areaServed": {"@type": "Country", "name": "Polska"},
            "offers": {"@type": "Offer", "name": "Konsultacja psychologiczna (60 minut)", "price": PRICE_SESSION, "priceCurrency": "PLN"},
        })
    elif kind == "article":
        graph.append({
            "@type": "Article",
            "@id": f"{url}#article",
            "headline": page["h1"],
            "description": page["description"],
            "inLanguage": "pl-PL",
            "datePublished": page["published"],
            "dateModified": page["updated"],
            "author": person_ref(),
            "publisher": org_ref(),
            "image": f"{SITE}/images/og-image.png",
            "mainEntityOfPage": {"@id": url},
        })
    if page.get("faq"):
        graph.append(faq_ld(url, page["faq"]))
    return graph


# --------------------------------------------------------------------------
# Elementy strony
# --------------------------------------------------------------------------

def faq_html(faq: list[list[str]]) -> str:
    items = "\n".join(
        f"""        <div class="faq-item">
          <button class="faq-question-btn" aria-expanded="false">
            <span class="faq-question-text">{esc(q)}</span>
            <span class="faq-icon-circle">{PLUS}</span>
          </button>
          <div class="faq-answer">
            <div class="faq-answer-inner">
              <p>{a}</p>
            </div>
          </div>
        </div>"""
        for q, a in faq
    )
    return f"""      <section class="article-faq" id="faq">
        <h2>Częste pytania</h2>
        <div class="faq-list">
{items}
        </div>
      </section>
"""


def card_html(page: dict, r: str, with_desc: bool = False) -> str:
    desc = f'\n          <span class="topic-desc">{esc(page["cardDesc"])}</span>' if with_desc and page.get("cardDesc") else ""
    return (
        f'        <a href="{r}{page["slug"]}" class="test-preview-card">\n'
        f'          <span class="test-card-tag">{esc(SECTIONS[page["type"]]["label"])}</span>\n'
        f'          <span class="test-card-title">{esc(page["card"])}</span>{desc}\n'
        f'        </a>'
    )


def related_html(page: dict, pages: list[dict], r: str) -> str:
    index = {p["slug"]: p for p in pages}
    picked = []
    for slug in page.get("related", []):
        if slug not in index:
            sys.exit(f'{page["source"]}: powiązana strona „{slug}” nie istnieje')
        picked.append(index[slug])
    if not picked:
        return ""
    cards = "\n".join(card_html(p, r) for p in picked)
    return f"""      <section class="related">
        <h2>Zobacz też</h2>
        <div class="related-grid">
{cards}
        </div>
      </section>
"""


def cta_band_html(page: dict, r: str) -> str:
    if page["type"] == "test":
        return f"""      <section class="cta-band">
        <div>
          <h2>Chcesz omówić wynik?</h2>
          <p>Bezpłatne 15 minut rozmowy online. Sprawdzimy, czy konsultacja ma w Twojej sytuacji sens.</p>
        </div>
        <a href="{r}index.html#kontakt" class="btn-cta">Umów bezpłatne 15 minut {ARROW_WHITE}</a>
      </section>
"""
    return f"""      <section class="cta-band">
        <div>
          <h2>Zacznij od bezpłatnych 15 minut</h2>
          <p>Krótka rozmowa online, bez zobowiązań. Pełna konsultacja trwa 60 minut i kosztuje {PRICE_SESSION} zł.</p>
        </div>
        <a href="{r}index.html#kontakt" class="btn-cta">Wybierz termin {ARROW_WHITE}</a>
      </section>
"""


def author_html(r: str) -> str:
    return f"""      <aside class="author-box" aria-label="O autorze">
        <img src="{r}images/kacper-760.webp" width="68" height="68" alt="Kacper Kulesza – psycholog" loading="lazy" decoding="async">
        <div>
          <strong>Kacper Kulesza, psycholog</strong>
          <p>Absolwent psychologii na Uniwersytecie SWPS. Prowadzi konsultacje psychologiczne online, korzystając z podejścia jednosesyjnego i technik poznawczo-behawioralnych (CBT). <a href="{r}index.html#o-mnie">Więcej o mnie</a></p>
        </div>
      </aside>
      <div class="crisis-note">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FF7A29" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"></circle><path d="M12 8v5"></path><path d="M12 16.5h.01"></path></svg>
        <p><strong>W kryzysie nie czekaj na wizytę.</strong> Jeśli masz myśli samobójcze albo czujesz, że nie jesteś bezpieczny, zadzwoń: <strong>112</strong> (numer alarmowy), <strong>116 123</strong> (telefon zaufania dla dorosłych) lub <strong>800 70 2222</strong> (całodobowe centrum wsparcia). Ta strona ma charakter edukacyjny i nie zastępuje diagnozy ani leczenia.</p>
      </div>
"""


def render_page(page: dict, pages: list[dict]) -> str:
    slug = page["slug"]
    r = depth_prefix(slug)
    url = f"{SITE}/{slug}"
    section = SECTIONS[page["type"]]
    page = dict(page, body=localize(page["body"], r), lead=localize(page["lead"], r),
                faq=[[q, localize(a, r)] for q, a in page.get("faq", [])])

    trail = [("Strona główna", f"{SITE}/")]
    crumbs = [f'<a href="{r}index.html">Strona główna</a>']
    if section["crumb"]:
        label, href = section["crumb"]
        trail.append((label, f"{SITE}/{href}"))
        crumbs.append(f'<a href="{r}{href}">{label}</a>')
    trail.append((page["card"], url))
    crumbs.append(f'<span aria-current="page">{esc(page["card"])}</span>')
    breadcrumbs = ' <span aria-hidden="true">›</span> '.join(crumbs)

    is_article = page["type"] == "article"
    extra_meta = ""
    if is_article:
        extra_meta = (f'  <meta property="article:published_time" content="{page["published"]}">\n'
                      f'  <meta property="article:modified_time" content="{page["updated"]}">\n'
                      f'  <meta property="article:author" content="Kacper Kulesza">')

    facts = ""
    if page.get("facts"):
        facts = '      <div class="fact-grid">\n' + "\n".join(
            f'        <div class="fact-item"><span class="fact-label">{esc(k)}</span><span class="fact-value">{esc(v)}</span></div>'
            for k, v in page["facts"]
        ) + "\n      </div>\n"

    cta_top = ""
    if page.get("testKey"):
        cta_top = f"""      <div class="article-cta-row">
        <a href="{r}testy.html#{page['testKey']}" class="btn-cta">Rozpocznij test {ARROW_WHITE}</a>
        <a href="{r}testy.html" class="btn-outline">Wszystkie testy {ARROW}</a>
      </div>
"""
    elif page["type"] in ("service", "problem"):
        second = (f'<a href="{r}konsultacja-psychologiczna-online.html" class="btn-outline">Jak wygląda konsultacja {ARROW}</a>'
                  if page["type"] == "problem" else f'<a href="{r}kontakt.html" class="btn-outline">Napisz lub zadzwoń {ARROW}</a>')
        cta_top = f"""      <div class="article-cta-row">
        <a href="{r}index.html#kontakt" class="btn-cta">Umów bezpłatne 15 minut {ARROW_WHITE}</a>
        {second}
      </div>
"""

    active = {"article": "Poradnik", "test": "Testy", "problem": "W czym pomagam", "service": ""}[page["type"]]
    faq = faq_html(page["faq"]) if page.get("faq") else ""
    meta_line = (f'<a href="{r}index.html#o-mnie">Kacper Kulesza</a>, psycholog · '
                 f'aktualizacja: <time datetime="{page["updated"]}">{pl_date(page["updated"])}</time>')

    return (
        head_html(title=page["title"], description=page["description"], canonical=url, r=r,
                  og_type="article" if is_article else "website", graph=page_graph(page, url, trail),
                  extra_meta=extra_meta)
        + '<body style="min-height: 100vh; display: flex; flex-direction: column;">\n\n'
        + header_html(r, active)
        + f"""
  <main id="main-content" class="article-main">
    <div class="bg-blob" style="top: -90px; left: -220px; width: 820px; height: 640px; background: radial-gradient(46% 48% at 46% 40%, rgba(28,134,238,.26) 0%, rgba(28,134,238,0) 72%), radial-gradient(40% 42% at 70% 64%, rgba(255,197,66,.2) 0%, rgba(255,197,66,0) 74%);"></div>
    <div class="bg-blob" style="top: 520px; right: -240px; width: 700px; height: 560px; background: radial-gradient(44% 46% at 50% 50%, rgba(255,122,41,.14) 0%, rgba(255,122,41,0) 74%);"></div>

    <article class="container article-container">
      <nav class="breadcrumbs" aria-label="Okruszki">{breadcrumbs}</nav>
      <span class="section-tag">{esc(page.get("tag", section["label"]))}</span>
      <h1>{esc(page["h1"])}</h1>
      <p class="article-meta">{meta_line}</p>
      <div class="answer-box">
        <p>{page["lead"]}</p>
      </div>
{facts}{cta_top}
      <div class="prose">
{page["body"]}
      </div>

{faq}{cta_band_html(page, r)}{related_html(page, pages, r)}{author_html(r)}    </article>
  </main>

"""
        + footer_html(pages, r)
        + "</body>\n</html>\n"
    )


def render_hub(pages: list[dict]) -> str:
    r = "../"
    url = f"{SITE}/poradnik/"
    articles = by_type(pages, "article")
    title = "Poradnik psychologiczny – konkretne odpowiedzi | Kacper Kulesza"
    description = ("Krótkie artykuły psychologa: do kogo iść z problemem, jak wygląda konsultacja online, "
                   "jak zatrzymać natłok myśli. Oparte na badaniach, bez ogólników.")
    updated = max(p["updated"] for p in articles)
    graph = [
        {
            "@type": "CollectionPage", "@id": url, "url": url, "name": title, "description": description,
            "inLanguage": "pl-PL", "isPartOf": {"@type": "WebSite", "@id": WEBSITE_ID}, "dateModified": updated,
            "author": person_ref(),
            "hasPart": [{"@type": "Article", "headline": p["h1"], "url": f'{SITE}/{p["slug"]}'} for p in articles],
        },
        breadcrumb_ld([("Strona główna", f"{SITE}/"), ("Poradnik", url)]),
    ]
    cards = "\n".join(card_html(p, r, with_desc=True) for p in articles)
    problems = "\n".join(card_html(p, r) for p in by_type(pages, "problem"))
    return (
        head_html(title=title, description=description, canonical=url, r=r, og_type="website", graph=graph)
        + '<body style="min-height: 100vh; display: flex; flex-direction: column;">\n\n'
        + header_html(r, "Poradnik")
        + f"""
  <main id="main-content" class="article-main">
    <div class="bg-blob" style="top: -90px; left: -220px; width: 820px; height: 640px; background: radial-gradient(46% 48% at 46% 40%, rgba(28,134,238,.26) 0%, rgba(28,134,238,0) 72%), radial-gradient(40% 42% at 70% 64%, rgba(255,197,66,.2) 0%, rgba(255,197,66,0) 74%);"></div>

    <div class="container" style="max-width: 1000px; position: relative;">
      <nav class="breadcrumbs" aria-label="Okruszki"><a href="{r}index.html">Strona główna</a> <span aria-hidden="true">›</span> <span aria-current="page">Poradnik</span></nav>
      <span class="section-tag">Poradnik</span>
      <h1>Poradnik psychologiczny</h1>
      <p style="margin-top: 16px; max-width: 62ch; font-size: 1.08rem;">Krótkie odpowiedzi na pytania, które najczęściej słyszę przed pierwszą rozmową. Każdy artykuł zaczyna się od konkretu i podaje źródła.</p>

      <div class="topic-grid">
{cards}
      </div>

      <section class="related">
        <h2>W czym pomagam</h2>
        <div class="related-grid">
{problems}
        </div>
      </section>

{cta_band_html({"type": "article"}, r)}    </div>
  </main>

"""
        + footer_html(pages, r)
        + "</body>\n</html>\n"
    )


# --------------------------------------------------------------------------
# sitemap.xml, llms.txt
# --------------------------------------------------------------------------

def write_sitemap(pages: list[dict], today: str) -> None:
    entries = [(f"{SITE}/{p['url']}", today) for p in STATIC_PAGES]
    entries.append((f"{SITE}/poradnik/", max(p["updated"] for p in by_type(pages, "article"))))
    entries += [(f'{SITE}/{p["slug"]}', p["updated"]) for p in pages]
    body = "\n".join(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{mod}</lastmod>\n  </url>" for loc, mod in entries)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "\n</urlset>\n",
        encoding="utf-8", newline="\n")


def write_llms(pages: list[dict]) -> None:
    def links(kind: str) -> str:
        return "\n".join(f'- [{p["card"]}]({SITE}/{p["slug"]}): {strip_tags(p["description"])}' for p in by_type(pages, kind))

    static = "\n".join(f'- [{p["title"]}]({SITE}/{p["url"]}): {p["desc"]}' for p in STATIC_PAGES)
    text = f"""# Kacper Kulesza – psycholog (konsultacje online)

> Kacper Kulesza jest psychologiem (dyplom z psychologii, Uniwersytet SWPS). Prowadzi konsultacje
> psychologiczne online dla osób z całej Polski. Jedna konsultacja trwa 60 minut, kosztuje {PRICE_SESSION} zł
> i dotyczy jednego konkretnego problemu; kończy się planem działania. Pierwsza rozmowa wstępna
> (15 minut) jest bezpłatna. To konsultacje psychologiczne, nie psychoterapia.

## Najważniejsze fakty
- Forma: wyłącznie online (wideorozmowa, link bez instalowania programów i zakładania konta)
- Rozmowa wstępna: 15 minut, 0 zł, bez zobowiązań
- Konsultacja psychologiczna: 60 minut, {PRICE_SESSION} zł
- Faktura: na życzenie
- Metody: podejście jednosesyjne oraz techniki poznawczo-behawioralne (CBT)
- Typowe tematy: natłok myśli i zamartwianie się, trudna decyzja, wypalenie zawodowe,
  konflikt w pracy lub w relacji, poczucie utknięcia
- Czego nie obejmuje: wieloletniej psychoterapii, leczenia uzależnień, diagnozy psychiatrycznej,
  leków ani zwolnień lekarskich
- Poufność: rozmowy objęte tajemnicą zawodową psychologa
- Język konsultacji: polski

## Kontakt i rezerwacja
- Rezerwacja terminu: {CALENDLY}
- Telefon: {PHONE_DISPLAY} (+48)
- E-mail: {EMAIL}
- Odpowiedź w ciągu 24 godzin w dni robocze
- Strona: {SITE}/
- TikTok: {TIKTOK}
- LinkedIn: {LINKEDIN}

## Oferta
{links("service")}

## W czym pomagam
{links("problem")}

## Bezpłatne testy psychologiczne
{links("test")}

## Poradnik
{links("article")}

## Pozostałe strony
{static}

## Uwaga
Testy na stronie są narzędziami przesiewowymi i nie stawiają diagnozy. W sytuacji zagrożenia życia:
112, 116 123 (telefon zaufania dla dorosłych), 800 70 2222 (całodobowe centrum wsparcia).
"""
    (ROOT / "llms.txt").write_text(text, encoding="utf-8", newline="\n")


def patch_static_footers(pages: list[dict]) -> None:
    """Odświeża mapę linków w stopkach stron pisanych ręcznie (między znacznikami)."""
    block = foot_sitemap_html(pages, "")
    pattern = re.compile(r"[ \t]*<!-- foot-sitemap:start.*?<!-- foot-sitemap:end -->", re.S)
    for name in ("index.html", "testy.html", "kontakt.html", "materialy.html"):
        path = ROOT / name
        with open(path, encoding="utf-8", newline="") as fh:
            text = fh.read()
        if pattern.search(text):
            # Zachowaj końce linii pliku (CRLF w kopii roboczej na Windows).
            eol = "\r\n" if "\r\n" in text else "\n"
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(pattern.sub(lambda _: block.replace("\n", eol), text, count=1))


def main() -> None:
    pages = load_pages()
    today = date.today().isoformat()
    for page in pages:
        out = ROOT / page["slug"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_page(page, pages), encoding="utf-8", newline="\n")
    (ROOT / "poradnik").mkdir(exist_ok=True)
    (ROOT / "poradnik" / "index.html").write_text(render_hub(pages), encoding="utf-8", newline="\n")
    write_sitemap(pages, today)
    write_llms(pages)
    patch_static_footers(pages)
    print(f"Zbudowano {len(pages)} podstron + hub poradnika, sitemap.xml, llms.txt")


if __name__ == "__main__":
    main()
