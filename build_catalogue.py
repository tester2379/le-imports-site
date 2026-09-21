"""L&E Imports website generator — brands, products, categories and filters.

DSM-1143. The instructions ask that L&E be able to add a brand or product later
and have it appear on its brand page, the Products page and the filters without
anyone redesigning a page. So the site is generated from ONE data file,
`LE Imports Website/data.json`, which was itself built from the two supplied
reference documents:

  * "L&E Imports Product images by brand"  — the 60 product images, each
    labelled with a Brand ID, Image ID, product name and original filename.
    That labelling is the only thing tying an image to a product, so it is the
    authority for which picture goes where.
  * "LE_Imports_Official_Brand_Logos_Final(1).docx" — the 15 approved logos.

To add a product: drop the image in assets/products/, add a row to data.json,
re-run this script. Nothing else changes.

Nothing about a product is invented here. Names, brands and images come from
the documents. Categories are assigned per brand from the list the instructions
permit. Only OYLUM and Vitaminka carry agency wording, because only those two
are identified that way in the supplied material. No prices appear anywhere,
and there is no basket or checkout — this is a B2B catalogue, as specified.
"""
import html
import json
import os
import shutil
from pathlib import Path

# The generator lives in the site it generates, so the repo carries the means
# to rebuild itself: `python build_catalogue.py` from this folder.
ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
BRANDS, PRODUCTS = DATA["brands"], DATA["products"]
CATEGORIES = DATA["categories"]

WA = ("https://wa.me/35699474578?text=Hello%2C%20I%20would%20like%20to%20request"
      "%20a%20quote%20from%20L%26E%20Imports.")
HERO = ("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d"
        "?auto=format&fit=crop&w=1800&q=85")
WAREHOUSE = ("https://images.unsplash.com/photo-1553413077-190dd305871c"
             "?auto=format&fit=crop&w=1200&q=85")

# The web font, lifted out of style.css so consent can gate it. Read from the
# file the extraction wrote, so the exact families and weights the design uses
# are preserved rather than retyped.
FONT_CSS = (ROOT / "FONT_URL.txt").read_text(encoding="utf-8").strip()

e = html.escape


def wa_link(text):
    """A Request-a-Quote link that tells L&E what the enquiry is about."""
    from urllib.parse import quote
    msg = f"Hello, I would like to request a quote from L&E Imports about: {text}"
    return "https://wa.me/35699474578?text=" + quote(msg)


def header(active, up=""):
    links = [("index.html", "Home", "home"),
             ("about.html", "About Us", "about"),
             ("brands.html", "Our Brands", "brands"),
             ("products.html", "Products", "products"),
             ("distribution.html", "Distribution & Services", "distribution"),
             ("contact.html", "Contact", "contact")]
    nav = "".join(
        f'<a class="{"active" if active == key else ""}" href="{up}{url}">{e(label)}</a>'
        for url, label, key in links)
    return (
        '<div class="notice-bar">L&amp;E Imports · B2B Food Importing &amp; Distribution '
        'across Malta</div>'
        '<header class="site-header"><div class="container nav-row">'
        f'<a class="brand" href="{up}index.html" aria-label="L&E Imports home">'
        '<span class="brand-mark">L&amp;E</span><span class="brand-name">IMPORTS</span></a>'
        f'<nav class="nav">{nav}</nav>'
        f'<a class="btn primary header-quote" href="{WA}" target="_blank" rel="noopener">'
        'Request a Quote <span>↗</span></a>'
        '<button class="menu-button" id="menuButton" aria-label="Open navigation" '
        'aria-expanded="false">☰</button></div></header>'
        f'<div class="mobile-nav" id="mobileNav">{nav}'
        f'<a class="btn primary" href="{WA}" target="_blank" rel="noopener">'
        'Request a Quote ↗</a></div>')


def footer(up=""):
    return (
        '<footer class="footer"><div class="container footer-grid"><div>'
        f'<a class="brand footer-brand" href="{up}index.html"><span class="brand-mark">L&amp;E</span>'
        '<span class="brand-name">IMPORTS</span></a>'
        '<p>Imported food, confectionery, snacks and beverages, distributed to '
        'supermarkets, retailers and commercial customers across Malta.</p></div>'
        f'<div><h3>Explore</h3><a href="{up}index.html">Home</a><a href="{up}about.html">About Us</a>'
        f'<a href="{up}brands.html">Our Brands</a><a href="{up}products.html">Products</a>'
        f'<a href="{up}distribution.html">Distribution &amp; Services</a>'
        f'<a href="{up}contact.html">Contact</a></div>'
        '<div><h3>Contact</h3><a href="tel:+35699474578">9947 4578</a>'
        '<a href="mailto:info@leimports.com">info@leimports.com</a>'
        '<span>46 Vjal il-Ħelsien<br>Ħaż-Żebbuġ, Malta<br>ZBG 2493</span></div>'
        '<div><h3>Start a conversation</h3><p>Tell us what your business needs and our '
        f'team will get back to you directly.</p><a class="btn light" href="{WA}" '
        'target="_blank" rel="noopener">Request a Quote ↗</a></div></div>'
        '<div class="container footer-bottom"><span>© 2026 L&amp;E Imports</span>'
        f'<span><a href="{up}privacy.html">Privacy Policy</a> · Website by '
        '<a href="https://dsmcomms.com/" target="_blank">DSM Communications</a></span></div></footer>')


def page(title, active, body, hero_title=None, hero_text=None, desc=None, up=""):
    """One page. NOTE the cookie notice: the generator that produced this site
    originally did not include it, so a rebuild silently stripped the GDPR
    banner and its privacy link from every page. It is part of the template
    now so that can't happen again."""
    hero = ""
    if hero_title:
        hero = ('<section class="page-hero" style="background-image:linear-gradient('
                f'90deg,rgba(41,38,95,.88),rgba(41,38,95,.38)),url({HERO})"><div class="container">'
                '<p class="eyebrow">L&amp;E IMPORTS</p>'
                f'<h1>{e(hero_title)}</h1>'
                + (f"<p>{e(hero_text)}</p>" if hero_text else "") + '</div></section>')
    description = desc or "L&E Imports — B2B food importing and distribution across Malta."
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<meta name="description" content="{e(description)}">'
        f'<title>{e(title)} · L&amp;E Imports</title>'
        f'<link rel="stylesheet" href="{up}style.css">'
        f'<link rel="stylesheet" href="{up}cookie-notice.css">'
        # Google Fonts held back until the visitor accepts. It used to be an
        # @import inside style.css, which loaded it for everyone the moment the
        # stylesheet parsed — so the cookie notice offered a "Refuse" that did
        # nothing. cookie-notice.js swaps data-consent-href to href on Accept.
        f'<link rel="stylesheet" data-consent-href="{FONT_CSS}">'
        f'</head><body>{header(active, up)}{hero}{body}{footer(up)}'
        f'<script src="{up}site.js"></script>'
        f'<script src="{up}cookie-notice.js" data-policy="{up}privacy.html" defer></script>'
        '</body></html>')


def brand_by_name(name):
    return next(b for b in BRANDS if b["name"] == name)


def products_of(brand_name):
    return [p for p in PRODUCTS if p["brand"] == brand_name]


# --------------------------------------------------------------- components
def logo_tile(b, up=""):
    return (f'<a class="logo-tile" href="{up}brands/{b["slug"]}/">'
            f'<img src="{up}{b["logo"]}" alt="{e(b["name"])} logo" loading="lazy">'
            f'<span class="logo-name">{e(b["name"])}</span>'
            f'<small>{b["count"]} product{"s" if b["count"] != 1 else ""}</small></a>')


def product_card(p, up=""):
    b = brand_by_name(p["brand"])
    return (f'<article class="product-card" data-brand="{e(b["slug"])}" '
            f'data-category="{e(p["category"])}">'
            f'<a class="product-shot" href="{up}products/{p["slug"]}/">'
            f'<img src="{up}{p["file"]}" alt="{e(p["name"])} — {e(p["brand"])}" loading="lazy"></a>'
            f'<div class="product-body"><span class="product-brand">{e(p["brand"])}</span>'
            f'<h3><a href="{up}products/{p["slug"]}/">{e(p["name"])}</a></h3>'
            f'<span class="product-cat">{e(p["category"])}</span>'
            f'<a class="btn secondary small" href="{wa_link(p["name"] + " (" + p["brand"] + ")")}" '
            'target="_blank" rel="noopener">Enquire ↗</a></div></article>')


# -------------------------------------------------------------------- pages
def build_home():
    picks = [p for p in PRODUCTS if p["id"] in
             ("B07-I011", "B06-I005", "B05-I005", "B10-I043", "B13-I054", "B01-I001",
              "B08-I035", "B14-I058")]
    picks = (picks + PRODUCTS)[:8]
    cards = "".join(product_card(p) for p in picks)
    logos = "".join(logo_tile(b) for b in BRANDS[:8])
    audience = "".join(
        f'<article class="audience-card"><span class="icon">{n}</span><h3>{t}</h3><p>{d}</p></article>'
        for n, t, d in [
            ("01", "Supermarkets", "Consistent access to international food, confectionery and beverage brands."),
            ("02", "Convenience stores", "Impulse lines and recognised brands that move off the shelf."),
            ("03", "Retailers", "A broad portfolio across confectionery, snacks, biscuits and drinks."),
            ("04", "Commercial customers", "Dependable supply for businesses across Malta.")])
    body = (
        f'<section class="hero" style="background-image:linear-gradient(90deg,'
        f'rgba(41,38,95,.9),rgba(41,38,95,.35)),url({HERO})"><div class="container hero-content">'
        '<p class="eyebrow">B2B FOOD IMPORTING &amp; DISTRIBUTION</p>'
        '<h1>Quality Products.<br><em>Reliable Distribution.</em></h1>'
        '<p class="lead">L&amp;E Imports imports and distributes food, confectionery, snacks '
        'and beverages to supermarkets, retailers and commercial customers across Malta.</p>'
        '<div class="actions"><a class="btn light" href="products.html">View Our Products ↗</a>'
        f'<a class="btn primary" href="{WA}" target="_blank" rel="noopener">Request a Quote ↗</a>'
        '</div></div></section>'
        '<section class="trust-strip"><div class="container trust-grid">'
        f'<span><b>{len(BRANDS)}</b> brands distributed</span>'
        f'<span><b>{len(PRODUCTS)}</b> products supplied</span>'
        '<span><b>2</b> official agency lines</span>'
        '<span><b>B2B</b> retail &amp; trade supply</span></div></section>'
        '<section class="section"><div class="container"><div class="split-head">'
        '<div><p class="eyebrow purple">OUR BRANDS</p><h2>The brands we<br>bring to Malta.</h2></div>'
        '<a class="text-link" href="brands.html">View all brands ↗</a></div>'
        f'<div class="logo-grid">{logos}</div>'
        '<p class="center-cta"><a class="btn secondary" href="brands.html">View All Brands ↗</a></p>'
        '</div></section>'
        '<section class="section offwhite"><div class="container"><div class="split-head">'
        '<div><p class="eyebrow purple">OUR PRODUCT RANGE</p>'
        '<h2>A selection from<br>across the portfolio.</h2></div>'
        '<a class="text-link" href="products.html">View all products ↗</a></div>'
        f'<div class="product-grid">{cards}</div>'
        '<p class="center-cta"><a class="btn secondary" href="products.html">View All Products ↗</a></p>'
        '</div></section>'
        '<section class="section"><div class="container"><div class="section-intro">'
        '<p class="eyebrow purple">WHO WE SUPPLY</p><h2>Built around the needs of<br>business buyers.</h2>'
        '<p>From the supermarket shelf to the convenience counter, L&amp;E Imports gives '
        'retailers across Malta reliable access to international food brands.</p></div>'
        f'<div class="audience-grid">{audience}</div></div></section>'
        '<section class="section dark"><div class="container cta-row">'
        '<div><p class="eyebrow">READY TO TALK SUPPLY?</p>'
        '<h2>Interested in stocking<br>these brands?</h2>'
        '<p>Tell us about your business and what you are looking for.</p></div>'
        f'<a class="btn primary" href="{WA}" target="_blank" rel="noopener">Request a Quote ↗</a>'
        '</div></section>')
    (ROOT / "index.html").write_text(
        page("Home", "home", body,
             desc="L&E Imports imports and distributes food, confectionery, snacks and "
                  "beverages to supermarkets and retailers across Malta."),
        encoding="utf-8")


def build_brands():
    tiles = "".join(logo_tile(b) for b in BRANDS)
    agency = [b for b in BRANDS if b["agency"]]
    agency_html = "".join(
        f'<article class="agency-card"><img src="{b["logo"]}" alt="{e(b["name"])} logo">'
        f'<div><h3>{e(b["name"])}</h3><p>Official agency and direct distribution in Malta.</p>'
        f'<a class="text-link" href="brands/{b["slug"]}/">View {e(b["name"])} range ↗</a></div>'
        '</article>' for b in agency)
    body = (
        '<section class="section"><div class="container"><div class="section-intro">'
        '<p class="eyebrow purple">THE PORTFOLIO</p><h2>Brands that bring<br>colour to the shelf.</h2>'
        f'<p>L&amp;E Imports distributes {len(BRANDS)} international brands across confectionery, '
        'chocolate, biscuits, snacks and beverages. Select a brand to see the products we supply.</p>'
        '</div>'
        '<div class="section-intro left"><p class="eyebrow purple">OFFICIAL AGENCY BRANDS</p></div>'
        f'<div class="agency-grid">{agency_html}</div>'
        f'<div class="logo-grid all">{tiles}</div></div></section>'
        '<section class="section dark"><div class="container cta-row">'
        '<div><p class="eyebrow">BRAND ENQUIRIES</p><h2>Interested in stocking<br>one of these brands?</h2>'
        '<p>Speak to us about availability and trade supply.</p></div>'
        f'<a class="btn primary" href="{WA}" target="_blank" rel="noopener">Request a Quote ↗</a>'
        '</div></section>')
    (ROOT / "brands.html").write_text(
        page("Our Brands", "brands", body, "Our Brands",
             "The international food, confectionery and beverage brands distributed by "
             "L&E Imports in Malta.",
             desc="The brands L&E Imports distributes across Malta, including official "
                  "agency lines OYLUM and Vitaminka."),
        encoding="utf-8")


def build_products():
    cards = "".join(product_card(p) for p in PRODUCTS)
    brand_opts = "".join(f'<option value="{e(b["slug"])}">{e(b["name"])}</option>' for b in BRANDS)
    cat_opts = "".join(f'<option value="{e(c)}">{e(c)}</option>' for c in CATEGORIES)
    body = (
        '<section class="section"><div class="container"><div class="section-intro">'
        '<p class="eyebrow purple">PRODUCT RANGE</p><h2>Everything we supply,<br>in one place.</h2>'
        f'<p>{len(PRODUCTS)} products across {len(BRANDS)} brands. Filter by brand or category, '
        'then send us an enquiry about anything you would like to stock. Trade enquiries only — '
        'this is a distribution catalogue, not an online shop.</p></div>'
        '<div class="filter-bar">'
        '<label>Brand<select id="filterBrand"><option value="">All brands</option>'
        f'{brand_opts}</select></label>'
        '<label>Category<select id="filterCategory"><option value="">All categories</option>'
        f'{cat_opts}</select></label>'
        '<button class="btn secondary small" id="filterReset" type="button">Reset</button>'
        f'<span class="filter-count" id="filterCount">{len(PRODUCTS)} products</span></div>'
        f'<div class="product-grid" id="productGrid">{cards}</div>'
        '<p class="no-results" id="noResults" hidden>No products match those filters.</p>'
        '</div></section>'
        '<section class="section dark"><div class="container cta-row">'
        '<div><p class="eyebrow">TRADE ENQUIRIES</p><h2>Want to stock<br>any of these?</h2>'
        '<p>Tell us which products you are interested in and we will come back to you.</p></div>'
        f'<a class="btn primary" href="{WA}" target="_blank" rel="noopener">Request a Quote ↗</a>'
        '</div></section>'
        '<script src="products.js"></script>')
    (ROOT / "products.html").write_text(
        page("Products", "products", body, "Products",
             "The full range of food, confectionery, snacks and beverages distributed by "
             "L&E Imports.",
             desc="Browse the products L&E Imports distributes in Malta, filterable by "
                  "brand and category."),
        encoding="utf-8")


def build_brand_pages():
    for b in BRANDS:
        items = products_of(b["name"])
        cards = "".join(product_card(p, "../../") for p in items)
        agency_note = ""
        if b["agency"]:
            agency_note = ('<p class="agency-flag">Official Agency &amp; Direct Distribution '
                           'in Malta</p>')
        body = (
            '<section class="section"><div class="container brand-head">'
            f'<div class="brand-logo-frame"><img src="../../{b["logo"]}" alt="{e(b["name"])} logo"></div>'
            f'<div><p class="eyebrow purple">BRAND</p><h1>{e(b["name"])}</h1>{agency_note}'
            f'<p>L&amp;E Imports supplies {len(items)} '
            f'{"product" if len(items) == 1 else "products"} from {e(b["name"])} to '
            'supermarkets, convenience stores and retailers across Malta.</p>'
            f'<a class="btn primary" href="{wa_link(b["name"])}" target="_blank" rel="noopener">'
            f'Interested in stocking {e(b["name"])}? ↗</a></div></div></section>'
            '<section class="section offwhite"><div class="container">'
            '<div class="section-intro left"><p class="eyebrow purple">PRODUCTS</p>'
            f'<h2>The {e(b["name"])} range</h2></div>'
            f'<div class="product-grid">{cards}</div>'
            '<p class="center-cta"><a class="btn secondary" href="../../brands.html">'
            '← All brands</a></p></div></section>')
        out = ROOT / "brands" / b["slug"]
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(
            page(b["name"], "brands", body, up="../../",
                 desc=f"{b['name']} products distributed by L&E Imports in Malta."),
            encoding="utf-8")


def build_product_pages():
    for p in PRODUCTS:
        b = brand_by_name(p["brand"])
        siblings = [s for s in products_of(p["brand"]) if s["id"] != p["id"]][:4]
        more = "".join(product_card(s, "../../") for s in siblings)
        more_html = ""
        if more:
            more_html = ('<section class="section offwhite"><div class="container">'
                         '<div class="section-intro left"><p class="eyebrow purple">MORE FROM '
                         f'{e(b["name"]).upper()}</p></div>'
                         f'<div class="product-grid">{more}</div></div></section>')
        body = (
            '<section class="section"><div class="container product-detail">'
            f'<div class="product-hero"><img src="../../{p["file"]}" '
            f'alt="{e(p["name"])} — {e(p["brand"])}"></div>'
            f'<div><a class="text-link" href="../../brands/{b["slug"]}/">'
            f'<img class="inline-logo" src="../../{b["logo"]}" alt=""> {e(p["brand"])}</a>'
            f'<h1>{e(p["name"])}</h1>'
            f'<p class="product-cat big">{e(p["category"])}</p>'
            f'<p>{e(p["name"])} is part of the {e(p["brand"])} range distributed by L&amp;E '
            'Imports to supermarkets, convenience stores and retailers across Malta. '
            'Contact us for trade availability and case quantities.</p>'
            f'<a class="btn primary" href="{wa_link(p["name"] + " (" + p["brand"] + ")")}" '
            'target="_blank" rel="noopener">Enquire About This Product ↗</a>'
            f'<p class="back-link"><a href="../../products.html">← All products</a> · '
            f'<a href="../../brands/{b["slug"]}/">All {e(p["brand"])} products</a></p>'
            '</div></div></section>' + more_html)
        out = ROOT / "products" / p["slug"]
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(
            page(p["name"], "products", body, up="../../",
                 desc=f"{p['name']} by {p['brand']}, distributed in Malta by L&E Imports."),
            encoding="utf-8")


def build_about():
    body = (
        '<section class="section"><div class="container split"><div>'
        '<p class="eyebrow purple">ABOUT L&amp;E IMPORTS</p>'
        '<h2>Connecting brands<br>with businesses.</h2>'
        '<p>L&amp;E Imports is a Malta-based importer and distributor of food, confectionery, '
        'snacks and beverages. We supply supermarkets, convenience stores, retailers and other '
        'commercial customers across the island.</p>'
        f'<p>Our portfolio has grown to {len(BRANDS)} international brands and {len(PRODUCTS)} '
        'products, spanning chocolate and confectionery, biscuits and cakes, savoury snacks, '
        'juices, energy drinks and grocery lines. For OYLUM and Vitaminka we act as official '
        'agent and direct distributor in Malta.</p>'
        '<p>Our role is straightforward: make quality imported products available to the '
        'businesses that sell them every day, with reliable supply and a direct line to our team.</p>'
        f'<a class="btn primary" href="{WA}" target="_blank" rel="noopener">Request a Quote ↗</a>'
        '</div><div class="image-frame">'
        f'<img src="{WAREHOUSE}" alt="Food distribution warehouse shelving"></div></div></section>'
        '<section class="section offwhite"><div class="container">'
        '<div class="section-intro left"><p class="eyebrow purple">OUR APPROACH</p>'
        '<h2>Professional supply,<br>without the unnecessary noise.</h2>'
        '<p>We keep the relationship direct: tell us what your business needs, and we will tell '
        'you what we can supply and how quickly.</p></div>'
        '<div class="principles">'
        '<article><b>01</b><h3>Product variety</h3><p>A broad and growing portfolio across '
        'confectionery, snacks and beverages.</p></article>'
        '<article><b>02</b><h3>Reliability</h3><p>Dependable supply for retailers who need '
        'their shelves filled.</p></article>'
        '<article><b>03</b><h3>Service</h3><p>A direct route to speak with the L&amp;E Imports '
        'team about any line.</p></article></div></div></section>'
        '<section class="section dark"><div class="container cta-row">'
        '<div><p class="eyebrow">WORK WITH US</p><h2>Looking for a reliable<br>supply partner?</h2>'
        '<p>Speak to us about the brands and products your business needs.</p></div>'
        f'<a class="btn primary" href="{WA}" target="_blank" rel="noopener">Request a Quote ↗</a>'
        '</div></section>')
    (ROOT / "about.html").write_text(
        page("About Us", "about", body, "About L&E Imports",
             "A Malta-based importer and distributor of international food, confectionery, "
             "snack and beverage brands."), encoding="utf-8")


def build_distribution():
    services = "".join(
        f'<article><span class="service-number">{n}</span><h3>{t}</h3><p>{d}</p></article>'
        for n, t, d in [
            ("01", "Food &amp; Beverage Importation",
             "We import food, confectionery, snacks and beverages into Malta from "
             "established international manufacturers."),
            ("02", "Retail Distribution",
             "Distribution to supermarkets, convenience stores and retailers across the island."),
            ("03", "Brand Representation",
             "We represent international brands in the Maltese market and bring them to trade buyers."),
            ("04", "Direct Distribution",
             "For OYLUM and Vitaminka we act as official agent and direct distributor in Malta."),
            ("05", "Supermarket &amp; Retail Supply",
             "Reliable supply for the businesses that stock our brands week to week.")])
    body = (
        '<section class="section"><div class="container split"><div>'
        '<p class="eyebrow purple">DISTRIBUTION &amp; SERVICES</p>'
        '<h2>More than a product list.</h2>'
        '<p>L&amp;E Imports is a supply and distribution partner for Malta\'s retail trade. '
        'We import international food and beverage brands and get them onto shelves across '
        'the island.</p>'
        '<p>Browse the <a href="brands.html">brands we distribute</a> or the full '
        '<a href="products.html">product range</a>, then talk to us about supply.</p>'
        f'<a class="btn primary" href="{WA}" target="_blank" rel="noopener">Request a Quote ↗</a>'
        '</div><div class="image-frame">'
        f'<img src="{WAREHOUSE}" alt="Warehouse distribution shelving"></div></div></section>'
        '<section class="section offwhite"><div class="container">'
        '<div class="section-intro left"><p class="eyebrow purple">WHAT WE DO</p>'
        '<h2>Focused on the business<br>behind the order.</h2></div>'
        f'<div class="service-grid">{services}</div>'
        '<p class="center-cta"><a class="btn secondary" href="products.html">View All Products ↗</a> '
        '<a class="btn secondary" href="brands.html">View All Brands ↗</a></p></div></section>'
        '<section class="section dark"><div class="container cta-row">'
        '<div><p class="eyebrow">B2B ENQUIRIES</p><h2>Let\'s discuss<br>your requirements.</h2>'
        '<p>Tell us which brands or products your business wants to stock.</p></div>'
        f'<a class="btn primary" href="{WA}" target="_blank" rel="noopener">Request a Quote ↗</a>'
        '</div></section>')
    (ROOT / "distribution.html").write_text(
        page("Distribution & Services", "distribution", body, "Distribution & Services",
             "Importation, retail distribution and brand representation across Malta."),
        encoding="utf-8")


def build_contact():
    body = (
        '<section class="section"><div class="container contact-layout"><div>'
        '<p class="eyebrow purple">CONTACT</p><h2>Talk to us about<br>stocking our brands.</h2>'
        '<p>L&amp;E Imports supplies supermarkets, convenience stores, retailers and other '
        'commercial customers across Malta. The quickest way to reach us is WhatsApp — tell us '
        'which brands or products you are interested in and we will come back to you.</p>'
        '<div class="contact-details">'
        '<a href="tel:+35699474578">9947 4578</a>'
        '<a href="mailto:info@leimports.com">info@leimports.com</a>'
        '<span>46 Vjal il-Ħelsien<br>Ħaż-Żebbuġ, Malta<br>ZBG 2493</span></div>'
        f'<a class="btn primary" href="{WA}" target="_blank" rel="noopener">Request a Quote ↗</a>'
        '</div><div class="form-card"><h3>What would you like to ask about?</h3>'
        '<p>Pick the closest option and it will open WhatsApp with your message started.</p>'
        f'<a class="btn secondary" href="{wa_link("stocking a brand")}" target="_blank" '
        'rel="noopener">Interested in Stocking a Brand? ↗</a>'
        f'<a class="btn secondary" href="{wa_link("a specific product")}" target="_blank" '
        'rel="noopener">Enquire About a Product ↗</a>'
        f'<a class="btn secondary" href="{wa_link("trade supply and distribution")}" '
        'target="_blank" rel="noopener">Trade Supply &amp; Distribution ↗</a>'
        '</div></div></section>')
    (ROOT / "contact.html").write_text(
        page("Contact", "contact", body, "Contact L&E Imports",
             "Trade enquiries from supermarkets, retailers and commercial customers in Malta."),
        encoding="utf-8")


def build_filter_js():
    (ROOT / "products.js").write_text(
        '// Products page filters (DSM-1143). Filtering is done on the cards already in\n'
        '// the page rather than by re-fetching, so it stays instant and works with the\n'
        '// site served as plain static files. Both selects narrow the same set.\n'
        '(function () {\n'
        '  "use strict";\n'
        '  var grid = document.getElementById("productGrid");\n'
        '  if (!grid) return;\n'
        '  var brand = document.getElementById("filterBrand");\n'
        '  var cat = document.getElementById("filterCategory");\n'
        '  var count = document.getElementById("filterCount");\n'
        '  var none = document.getElementById("noResults");\n'
        '  var reset = document.getElementById("filterReset");\n'
        '  var cards = Array.prototype.slice.call(grid.querySelectorAll(".product-card"));\n'
        '\n'
        '  function apply() {\n'
        '    var b = brand.value, c = cat.value, shown = 0;\n'
        '    cards.forEach(function (card) {\n'
        '      var ok = (!b || card.dataset.brand === b) && (!c || card.dataset.category === c);\n'
        '      card.hidden = !ok;\n'
        '      if (ok) shown++;\n'
        '    });\n'
        '    count.textContent = shown + (shown === 1 ? " product" : " products");\n'
        '    none.hidden = shown !== 0;\n'
        '  }\n'
        '  brand.addEventListener("change", apply);\n'
        '  cat.addEventListener("change", apply);\n'
        '  reset.addEventListener("click", function () {\n'
        '    brand.value = ""; cat.value = ""; apply();\n'
        '  });\n'
        '})();\n', encoding="utf-8")


if __name__ == "__main__":
    build_home()
    build_about()
    build_brands()
    build_products()
    build_brand_pages()
    build_product_pages()
    build_distribution()
    build_contact()
    build_filter_js()
    pages = len(list(ROOT.rglob("index.html"))) + len(list(ROOT.glob("*.html")))
    print(f"brands {len(BRANDS)} · products {len(PRODUCTS)} · categories {len(CATEGORIES)}")
    print(f"generated {len(BRANDS)} brand pages + {len(PRODUCTS)} product pages + 6 top-level pages")
