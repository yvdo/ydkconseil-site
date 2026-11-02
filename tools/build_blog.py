#!/usr/bin/env python3
"""Génère le blog YDK Conseil à partir de content/blog/*.html.

Chaque fichier commence par un commentaire JSON (front matter) :
<!--{"slug": "...", "title": "...", "seo_title": "...", "description": "...",
     "category": "...", "date": "AAAA-MM-JJ", "excerpt": "...", "keywords": [...]}-->
suivi du corps de l'article en HTML (balises <h2> pour les sections).

Produit :
  public/blog/<slug>/index.html   une page par article
  public/blog/index.html          la liste des articles
  public/sitemap.xml              régénéré avec toutes les pages
  public/index.html               bloc « Derniers articles » (entre les marqueurs BLOG)

Usage : python3 tools/build_blog.py
"""
import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "blog"
PUBLIC = ROOT / "public"
SITE = "https://ydkconseil.com"
CSS_V = "3"
JS_V = "3"
AUTHOR = "Yves-Donatien Kadjo"
PHOTO = "/assets/img/yves-donatien-kadjo-product-manager-freelance-480.jpg"
OG = f"{SITE}/assets/img/og-ydk-conseil.jpg"
MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
          "août", "septembre", "octobre", "novembre", "décembre"]


def fr_date(iso):
    y, m, d = map(int, iso.split("-"))
    return f"{d} {MONTHS[m - 1]} {y}"


def typo(text):
    """Espaces insécables de la typographie française (avant : ; ? ! », après «)."""
    text = re.sub(r" ([:;?!»])", "\u00a0\\1", text)
    return text.replace("« ", "«\u00a0")


def slugify(text):
    text = text.lower()
    for a, b in (("àâä", "a"), ("éèêë", "e"), ("îï", "i"), ("ôö", "o"), ("ùûü", "u"), ("ç", "c"), ("œ", "oe")):
        for ch in a:
            text = text.replace(ch, b)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:60]


def load_posts():
    posts = []
    for f in sorted(CONTENT.glob("*.html")):
        raw = f.read_text(encoding="utf-8")
        m = re.match(r"\s*<!--(\{.*?\})-->\s*(.*)", raw, re.S)
        if not m:
            raise SystemExit(f"Front matter manquant : {f.name}")
        meta = json.loads(m.group(1))
        body = typo(m.group(2).strip())
        for k in ("title", "excerpt"):
            meta[k] = typo(meta[k])
        toc = []

        def add_id(mm):
            attrs, inner = mm.group(1), mm.group(2)
            if 'id="' in attrs:
                hid = re.search(r'id="([^"]+)"', attrs).group(1)
            else:
                hid = slugify(inner)
                attrs = f' id="{hid}"' + attrs
            toc.append((hid, re.sub(r"<[^>]+>", "", inner)))
            return f"<h2{attrs}>{inner}</h2>"

        body = re.sub(r"<h2([^>]*)>(.*?)</h2>", add_id, body, flags=re.S)
        words = len(re.sub(r"<[^>]+>", " ", body).split())
        meta.update(body=body, toc=toc, minutes=max(3, round(words / 220)), words=words)
        meta.setdefault("updated", meta["date"])
        posts.append(meta)
    posts.sort(key=lambda p: (p["date"], p.get("order", 0)), reverse=True)
    return posts


def head(title, description, canonical, og_type="website", extra=""):
    t, d = html.escape(title), html.escape(description)
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="author" content="{AUTHOR}">
<meta name="theme-color" content="#1C1917">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="YDK Conseil">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:image" content="{OG}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="{OG}">
{extra}<link rel="alternate" type="application/rss+xml" title="Blog YDK Conseil" href="/blog/feed.xml">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&amp;family=Geist:wght@400;500;600&amp;family=Geist+Mono:wght@400;500&amp;display=swap">
<link rel="stylesheet" href="/assets/css/style.css?v={CSS_V}">
<script src="/assets/js/main.js?v={JS_V}" defer></script>
"""


HEADER = """<a class="skip" href="#contenu">Aller au contenu</a>
<div class="progress" aria-hidden="true"></div>
<header class="site-header">
  <div class="wrap">
    <a href="/" class="logo" aria-label="YDK Conseil, accueil"><b>YDK</b><span>CONSEIL</span></a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu" aria-label="Ouvrir le menu">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1C1917" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path class="l1" d="M4 8h16"/><path class="l2" d="M4 16h16"/></svg>
    </button>
    <nav id="menu" class="nav" aria-label="Navigation principale">
      <a href="/#offres" class="link-ul">Offres</a>
      <a href="/#expertises" class="link-ul">Expertises</a>
      <a href="/#cas-clients" class="link-ul">Cas clients</a>
      <a href="/blog/" class="link-ul"{blog_current}>Blog</a>
      <a href="/#apropos" class="link-ul">À propos</a>
      <a href="/#contact" class="btn btn-dark">Réserver un appel</a>
    </nav>
  </div>
</header>
"""

FOOTER = """<footer class="site-footer">
  <div class="wrap">
    <span>© <span id="year">2026</span> YDK Conseil · Product Manager freelance</span>
    <nav aria-label="Liens de pied de page">
      <a href="/blog/" class="link-ul">Blog</a>
      <a href="/mentions-legales.html" class="link-ul">Mentions légales</a>
      <a href="https://www.linkedin.com/in/yvesdonatien-kadjo/" class="link-ul" rel="noopener" target="_blank">LinkedIn</a>
      <a href="https://ydkagency.com" class="link-ul">Besoin d'un site ou d'automatisations ? YDK Agency →</a>
    </nav>
  </div>
</footer>
<div class="mobile-bar">
  <a href="/#contact" class="btn btn-dark">Réserver un appel</a>
  <a href="mailto:contact@ydkconseil.com" class="icon-btn" aria-label="Écrire un email">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1C1917" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>
  </a>
</div>
</body>
</html>
"""


def ld(obj):
    return '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=2) + "\n</script>\n"


def card(p, heading="h2", d=0):
    e = html.escape
    return f"""    <a class="card post-card rv" style="--d:{d}" href="/blog/{p['slug']}/">
      <p class="meta"><span class="cat">{e(p['category'])}</span><span>{fr_date(p['date'])}</span><span>{p['minutes']} min</span></p>
      <{heading}>{e(p['title'])}</{heading}>
      <p>{e(p['excerpt'])}</p>
      <span class="more">Lire l'article →</span>
    </a>"""


def article_page(p, posts):
    e = html.escape
    url = f"{SITE}/blog/{p['slug']}/"
    related = [q for q in posts if q["slug"] in p.get("related", [])] or [q for q in posts if q["slug"] != p["slug"]]
    related = related[:3]
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BlogPosting",
                "@id": url + "#article",
                "headline": p["title"],
                "description": p["description"],
                "datePublished": p["date"],
                "dateModified": p["updated"],
                "inLanguage": "fr-FR",
                "wordCount": p["words"],
                "articleSection": p["category"],
                "keywords": ", ".join(p.get("keywords", [])),
                "image": OG,
                "mainEntityOfPage": url,
                "author": {"@type": "Person", "@id": f"{SITE}/#yves-donatien", "name": AUTHOR,
                           "url": f"{SITE}/#apropos", "jobTitle": "Product Manager freelance",
                           "sameAs": ["https://www.linkedin.com/in/yvesdonatien-kadjo/"]},
                "publisher": {"@type": "Organization", "@id": f"{SITE}/#organisation", "name": "YDK Conseil",
                              "logo": {"@type": "ImageObject", "url": f"{SITE}/icon-512.png"}},
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f"{SITE}/"},
                    {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog/"},
                    {"@type": "ListItem", "position": 3, "name": p["title"], "item": url},
                ],
            },
        ],
    }
    toc = "\n".join(f'        <li><a href="#{hid}">{e(label)}</a></li>' for hid, label in p["toc"])
    rel = "\n".join(card(q, "h3", i) for i, q in enumerate(related))
    extra = f'<meta property="article:published_time" content="{p["date"]}">\n<meta property="article:modified_time" content="{p["updated"]}">\n<meta property="article:author" content="{AUTHOR}">\n<meta property="article:section" content="{e(p["category"])}">\n'
    extra += "".join(f'<meta property="article:tag" content="{e(k)}">\n' for k in p.get("keywords", []))
    return (head(p["seo_title"], p["description"], url, "article", extra) + ld(graph) + "</head>\n<body>\n"
            + HEADER.replace("{blog_current}", ' aria-current="page"') + f"""
<main id="contenu">
<article>
  <header class="article-head">
    <nav class="crumbs" aria-label="Fil d'Ariane"><ol><li><a href="/">Accueil</a></li><li><a href="/blog/">Blog</a></li><li aria-current="page">{e(p['category'])}</li></ol></nav>
    <h1>{e(p['title'])}</h1>
    <p class="standfirst">{e(p['excerpt'])}</p>
    <div class="byline">
      <img src="{PHOTO}" alt="" width="48" height="48" loading="lazy">
      <div><strong>{AUTHOR}</strong>Product Manager freelance · <time datetime="{p['date']}">{fr_date(p['date'])}</time> · {p['minutes']} min de lecture</div>
    </div>
  </header>
  <div class="article-layout">
    <nav class="toc" aria-label="Sommaire">
      <p>Sommaire</p>
      <ol>
{toc}
      </ol>
    </nav>
    <div>
      <div class="prose">
{p['body']}
      </div>
      <aside class="author-box" aria-label="À propos de l'auteur">
        <img src="{PHOTO}" alt="{AUTHOR}" width="72" height="72" loading="lazy">
        <div><strong>{AUTHOR}</strong><p>Dix ans en produit, d'abord comme Product Owner puis comme Product Manager, aujourd'hui en freelance. J'ai notamment porté les parcours de vente en ligne de Stellantis (+40 % de conversion). J'aide les équipes à cadrer, prioriser et livrer ce qui fait bouger la performance.</p></div>
      </aside>
      <section class="cta-box" aria-label="Contact">
        <div>
          <h2>Un sujet produit à débloquer ?</h2>
          <p>30 minutes pour en parler, sans engagement. Réponse sous 48 h.</p>
        </div>
        <a href="/#contact" class="btn btn-amber">Réserver un échange
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg></a>
      </section>
    </div>
  </div>
</article>
<section class="wrap related" aria-labelledby="t-related">
  <p class="eyebrow">À lire aussi</p>
  <h2 id="t-related" class="h2 mb44">Pour aller plus loin.</h2>
  <div class="post-grid">
{rel}
  </div>
</section>
</main>
""" + FOOTER)


def index_page(posts):
    url = f"{SITE}/blog/"
    desc = "Le blog de YDK Conseil : product management, priorisation, product discovery, conversion e-commerce et génération de leads. Méthodes concrètes et retours d'expérience."
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Blog", "@id": url + "#blog", "url": url, "name": "Blog YDK Conseil — Product management, conversion & leads",
             "description": desc, "inLanguage": "fr-FR", "publisher": {"@id": f"{SITE}/#organisation"},
             "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": f"{url}{p['slug']}/", "datePublished": p["date"]} for p in posts]},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": "Blog", "item": url}]},
        ],
    }
    cards = "\n".join(card(p, "h2", i % 3) for i, p in enumerate(posts))
    return (head("Blog product management, conversion & leads | YDK Conseil", desc, url) + ld(graph) + "</head>\n<body>\n"
            + HEADER.replace("{blog_current}", ' aria-current="page"') + f"""
<main id="contenu">
  <section class="wrap blog-hero">
    <nav class="crumbs" aria-label="Fil d'Ariane"><ol><li><a href="/">Accueil</a></li><li aria-current="page">Blog</li></ol></nav>
    <h1>Le blog <span class="italic accent">produit</span>.</h1>
    <p class="lead">Product management, priorisation, discovery, conversion e-commerce et génération de leads : des méthodes concrètes, testées sur le terrain, pour faire avancer votre produit dans la bonne direction.</p>
  </section>
  <section class="wrap" style="padding-bottom:clamp(56px,8vw,104px)" aria-label="Articles">
    <div class="post-grid">
{cards}
    </div>
  </section>
</main>
""" + FOOTER)


def feed(posts):
    items = "".join(f"""  <item>
    <title>{html.escape(p['title'])}</title>
    <link>{SITE}/blog/{p['slug']}/</link>
    <guid>{SITE}/blog/{p['slug']}/</guid>
    <pubDate>{date.fromisoformat(p['date']).strftime('%a, %d %b %Y')} 08:00:00 +0100</pubDate>
    <description>{html.escape(p['excerpt'])}</description>
  </item>
""" for p in posts)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>Blog YDK Conseil</title>
  <link>{SITE}/blog/</link>
  <description>Product management, conversion e-commerce et génération de leads.</description>
  <language>fr-FR</language>
{items}</channel>
</rss>
"""


def sitemap(posts):
    today = date.today().isoformat()
    newest = max([p["updated"] for p in posts] + [today])
    urls = [(f"{SITE}/", today), (f"{SITE}/blog/", newest)]
    urls += [(f"{SITE}/blog/{p['slug']}/", p["updated"]) for p in posts]
    urls += [(f"{SITE}/mentions-legales.html", "2026-11-02")]
    body = "".join(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{d}</lastmod>\n  </url>\n" for u, d in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}</urlset>\n'


def update_home(posts):
    f = PUBLIC / "index.html"
    h = f.read_text(encoding="utf-8")
    cards = "\n".join(card(p, "h3", i) for i, p in enumerate(posts[:3]))
    block = f"""<!-- BLOG:START -->
<section id="blog" class="wrap section" aria-labelledby="t-blog">
  <div class="section-head">
    <div>
      <p class="eyebrow rv">Blog</p>
      <h2 id="t-blog" class="h2 rv" style="--d:1">Méthodes et retours d'expérience produit.</h2>
    </div>
    <p class="rv" style="--d:2"><a href="/blog/" class="link-ul" style="font-weight:500;color:var(--ink)">Tous les articles →</a></p>
  </div>
  <div class="post-grid">
{cards}
  </div>
</section>
<!-- BLOG:END -->"""
    h, n = re.subn(r"<!-- BLOG:START -->.*?<!-- BLOG:END -->", block, h, flags=re.S)
    if n != 1:
        raise SystemExit("Marqueurs BLOG introuvables dans public/index.html")
    f.write_text(h, encoding="utf-8")


def main():
    posts = load_posts()
    for p in posts:
        out = PUBLIC / "blog" / p["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(article_page(p, posts), encoding="utf-8")
    (PUBLIC / "blog" / "index.html").write_text(index_page(posts), encoding="utf-8")
    (PUBLIC / "blog" / "feed.xml").write_text(feed(posts), encoding="utf-8")
    (PUBLIC / "sitemap.xml").write_text(sitemap(posts), encoding="utf-8")
    update_home(posts)
    for p in posts:
        print(f"{p['date']}  {p['minutes']:>2} min  {p['words']:>5} mots  /blog/{p['slug']}/")


if __name__ == "__main__":
    main()
