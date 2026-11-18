"""Every page of the Jade Astrology site, as plain HTML.

The look, wording and page addresses follow the live jadeastrology.com (the WordPress
theme and the Jade Horoscopes plugin), rebuilt without WordPress or DivineAPI.
"""
import datetime as dt
import html
import json
import os
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
YEAR = "2027"
SIGNS = ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio",
         "sagittarius", "capricorn", "aquarius", "pisces"]
PLURAL = {"aries": "Aries", "taurus": "Taurus", "gemini": "Geminis", "cancer": "Cancers", "leo": "Leos",
          "virgo": "Virgos", "libra": "Libras", "scorpio": "Scorpios", "sagittarius": "Sagittarians",
          "capricorn": "Capricorns", "aquarius": "Aquarians", "pisces": "Pisces"}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December"]
SECTION_LABELS = [("personal", "Personal life"), ("emotions", "Emotions"), ("profession", "Career"),
                  ("health", "Health & wellbeing"), ("travel", "Travel")]
MARK = ('<svg class="site-brand__mark" viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="15" '
        'fill="#1F6F5A"/><circle cx="16" cy="16" r="10.5" fill="none" stroke="#E2C77A" stroke-width="1" '
        'opacity=".6"/><path d="M16 7.5l2.1 6.4 6.4 2.1-6.4 2.1L16 24.5l-2.1-6.4L7.5 16l6.4-2.1z" fill="#F1D58A"/></svg>')
BRAND = "Jade Astrology"
COMPANY = "Bluesio LLC"
ADDRESS = "212 N. 2nd St. STE 100, Richmond, KY 40475, USA"
EMAIL = "support@jadeastrology.com"
BIRTHS_PER_DAY = 360000


def e(s):
    return html.escape(str(s), quote=True)


def ordinal(n):
    return f"{n}{'th' if 11 <= n % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def pair_key(a, b):
    """aries+leo -> ('aries', 'leo'): always in zodiac order."""
    ia, ib = SIGNS.index(a), SIGNS.index(b)
    return (a, b) if ia <= ib else (b, a)


def pair_slug(a, b):
    a, b = pair_key(a, b)
    return f"{a}-and-{b}-compatibility"


class Site:
    def __init__(self, cfg, ref, copy, horoscopes, compat, now):
        self.cfg = cfg
        self.domain = cfg["domain"]
        self.test = cfg["brain_url"] == "test"
        self.ref = ref
        self.signs = ref["signs"]
        self.naks = ref["nakshatras"]
        self.copy = copy
        self.now = now
        self.offers = json.load(open(os.path.join(HERE, "data", "offers.json"), encoding="utf-8"))
        self.h = horoscopes or self.sample_horoscopes()
        self.c = compat or self.sample_compat()
        self.files = {}
        self.sitemap = []

    # ------------------------------------------------------------------ helpers
    def url(self, slug=""):
        return f"https://{self.domain}/{slug + '/' if slug else ''}"

    def link(self, slug):
        return f"/{slug}/" if slug else "/"

    def sname(self, s):
        return self.signs[s]["name"]

    def symbol(self, s):
        return self.signs[s]["symbol"]

    def today_label(self):
        return self.now.strftime("%A, %B %-d, %Y")

    def week_start(self):
        d = self.now.date()
        return d - dt.timedelta(days=(d.weekday() + 1) % 7)  # Sunday

    def add(self, slug, title, desc, body, noindex=False, main_class="jade-route-main", sitemap=True):
        path = "index.html" if slug == "" else f"{slug}/index.html"
        self.files[path] = self.layout(slug, title, desc, body, noindex, main_class)
        if sitemap and not noindex:
            self.sitemap.append(slug)

    # ------------------------------------------------------------------ layout
    def layout(self, slug, title, desc, body, noindex, main_class):
        head_extra = ""
        if noindex:
            head_extra += '<meta name="robots" content="noindex, nofollow">\n<meta name="referrer" content="no-referrer">\n'
        else:
            head_extra += f'<link rel="canonical" href="{e(self.url(slug))}">\n'
        if desc:
            head_extra += f'<meta name="description" content="{e(desc)}">\n'
        cfg = {"brain": "" if self.test else self.cfg["brain_url"].rstrip("/"), "site": self.cfg["site_id"],
               "test": self.test, "brand": BRAND, "home": "/", "births": BIRTHS_PER_DAY, "email": EMAIL}
        mock = '<script src="/assets/jade-mock.js" defer></script>\n' if self.test else ""
        nav = [("horoscope-today", "Horoscope today"), ("weekly-horoscope", "Weekly"),
               ("monthly-horoscope", "Monthly"), ("compatibility-calculator", "Compatibility"), ("birth-chart-calculator", "Birth chart"),
               ("free-reading", "Free reading")]
        cur = ' class="current-menu-item"'
        nav_html = "".join(f'<li{cur if s == slug else ""}><a href="{self.link(s)}">{e(t)}</a></li>' for s, t in nav)
        return f"""<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
{head_extra}<meta name="theme-color" content="#0B1F2A">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/jade.css">
<script>window.JadeCfg = {json.dumps(cfg)};</script>
{mock}<script src="/assets/jade.js" defer></script>
</head>
<body>
<a class="skip-link screen-reader-text" href="#primary">Skip to content</a>
<header class="site-header">
	<div class="site-header__in">
		<a class="site-brand" href="/" rel="home">{MARK}<span>{BRAND}</span></a>
		<button class="nav-toggle" type="button" aria-controls="site-nav" aria-expanded="false">Menu</button>
		<nav id="site-nav" class="site-nav" aria-label="Main"><ul>{nav_html}</ul></nav>
	</div>
</header>
<main id="primary" class="site-main {main_class}">
{body}
</main>
{self.footer()}
</body>
</html>
"""

    def footer(self):
        cols = [
            ("Horoscopes", [("horoscope-today", "Horoscope today"), ("weekly-horoscope", "Weekly horoscope"),
                            ("monthly-horoscope", "Monthly horoscope"), (f"{YEAR}-horoscope", f"{YEAR} horoscope"), ("love-horoscope", "Love horoscope")]),
            ("Calculators", [("birth-chart-calculator", "Birth chart"), ("rising-sign-calculator", "Rising sign"),
                             ("moon-sign-calculator", "Moon sign"), ("big-three-calculator", "Big three"),
                             ("saturn-return-calculator", "Saturn return")]),
            ("Compatibility", [("compatibility-calculator", "Compatibility calculator"),
                               ("love-calculator", "Love calculator"), ("zodiac-compatibility", "Zodiac compatibility"),
                               ("synastry-calculator", "Synastry calculator")]),
            ("Vedic", [("vedic-birth-chart", "Vedic birth chart"), ("kundli-online", "Kundli online"),
                       ("nakshatra-calculator", "Nakshatra calculator")]),
            ("Life", [("when-will-i-get-married", "When will I get married?"), ("career-astrology", "Career astrology"),
                      ("money-horoscope", "Money horoscope")]),
        ]
        out = '<footer class="site-footer">\n<div class="site-footer__links">'
        for h, links in cols:
            out += f"<div><h2>{e(h)}</h2><ul>" + "".join(
                f'<li><a href="{self.link(s)}">{e(t)}</a></li>' for s, t in links) + "</ul></div>"
        out += "</div>\n"
        legal = [("about", "About"), ("contact", "Contact"), ("pricing", "Pricing"), ("privacy-policy", "Privacy"),
                 ("terms", "Terms"), ("refund-policy", "Refunds"), ("disclaimer", "Disclaimer")]
        out += '<div class="jade-footer"><nav aria-label="Legal">' + "".join(
            f'<a href="{self.link(s)}">{e(t)}</a>' for s, t in legal) + "</nav>"
        out += ("<p>Horoscopes and readings are calculated from astronomical data using traditional Vedic and Western "
                "methods, and are offered for personal guidance and self-reflection. They are not a substitute for "
                "professional medical, legal, financial or psychological advice.</p>")
        out += f"<p>&copy; {self.now.year} {COMPANY}. {BRAND} is a brand of {COMPANY}, {e(ADDRESS)}.</p></div>\n</footer>"
        return out

    # ------------------------------------------------------------------ funnel copy
    def fill(self, text, sign, when="today", when_label="today"):
        i = SIGNS.index(sign) if sign else None
        return (text.replace("{Sign}", self.sname(sign) if sign else "your sign")
                .replace("{Signs}", PLURAL[sign] if sign else "people")
                .replace("{Prev}", self.sname(SIGNS[(i + 11) % 12]) if sign else "")
                .replace("{when_label}", when_label).replace("{when}", when))

    def when_label(self, when):
        if when == "tomorrow":
            return (self.now + dt.timedelta(days=1)).strftime("%A, %B %-d")
        if when == "this week":
            return "the week of " + self.week_start().strftime("%B %-d")
        if when == "this month":
            return self.now.strftime("%B %Y")
        return "today, " + self.now.strftime("%A, %B %-d")

    # ------------------------------------------------------------------ the free-reading funnel
    def funnel(self, intent="general", head="", sub="", tag="h2", sign="", when="today", topic="",
               focus="", source="", show_head=True, eyebrow="Free · about 30 seconds · no email needed"):
        if not topic:
            topic = "love" if intent in ("love", "marriage") else (intent if intent in ("career", "money") else "general")
        if not focus:
            focus = "saturn" if intent == "saturn" else (YEAR if intent == "year" else "")
        wl = self.when_label(when)
        row = self.copy.get(intent + "_sign") if sign and (intent + "_sign") in self.copy else None
        row = row or self.copy.get(intent) or self.copy["general"]
        variants = dict(row["headlines"])
        if "a" not in variants and head:
            variants = {"a": head, **variants}
        variants = {k: self.fill(v, sign, when, wl) for k, v in sorted(variants.items())}
        first = next(iter(variants.values()))
        sub = self.fill(row["sub"], sign, when, wl)  # the copy table's line, as on the live site
        button = self.fill(row["button"], sign, when, wl)
        attrs = (f' data-intent="{e(intent)}" data-when="{e(when)}" data-topic="{e(topic)}" data-focus="{e(focus)}"'
                 f' data-source="{e(source)}"')
        if sign:
            attrs += f' data-sign="{e(sign)}"'
        if len(variants) > 1:
            attrs += f' data-variants="{e(json.dumps(variants))}"'
        months = "".join(f'<option value="{i + 1}">{m}</option>' for i, m in enumerate(MONTHS))
        days = "".join(f'<option value="{d}">{d}</option>' for d in range(1, 32))
        years = "".join(f'<option value="{y}">{y}</option>' for y in range(self.now.year, 1919, -1))
        uid = f"jf-{zlib.crc32((source + intent + sign + when).encode()) % 100000}"
        topics_pre = {"love": "love", "career": "career", "money": "money"}.get(topic, "")
        def tchk(v):
            return " checked" if v == topics_pre else ""
        head_html = ""
        if show_head:
            head_html = (f'<div class="jf-head"><p class="jade-eyebrow">{e(eyebrow)}</p>'
                         f'<{tag} class="jf-title" data-jade-kw-head>{e(first)}</{tag}>'
                         f'<p class="jf-sub" data-jade-kw-sub>{e(sub)}</p></div>')
        return f"""<section class="jade-funnel" data-jade-funnel{attrs}>
{head_html}
<div class="jf-box">
<div class="jf-progress" aria-hidden="true"><span></span></div>
<form class="jf-form" novalidate>
<fieldset class="jf-step" data-step="date">
	<legend>When were you born?</legend>
	<div class="jf-row3">
		<label class="jade-field"><span>Month</span><select name="b_month" required><option value="">Month</option>{months}</select></label>
		<label class="jade-field"><span>Day</span><select name="b_day" required><option value="">Day</option>{days}</select></label>
		<label class="jade-field"><span>Year</span><select name="b_year" required><option value="">Year</option>{years}</select></label>
	</div>
	<div class="jf-nav"><button type="button" class="jade-btn" data-next>Next</button></div>
</fieldset>
<fieldset class="jf-step" data-step="place" hidden>
	<legend>Where were you born?</legend>
	{self.place_field(uid)}
	<p class="jade-small jade-muted">Your birthplace sets your local time and the angle of the sky. It changes your chart more than most people think.</p>
	<div class="jf-nav"><button type="button" class="jade-link" data-back>Back</button><button type="button" class="jade-btn" data-next>Next</button></div>
</fieldset>
<fieldset class="jf-step" data-step="time" hidden>
	<legend>What time were you born?</legend>
	<div class="jf-choices" role="radiogroup">
		<label class="jf-choice"><input type="radio" name="time_mode" value="exact" checked><span>I know my birth time</span></label>
		<label class="jf-choice"><input type="radio" name="time_mode" value="rough"><span>I know roughly</span></label>
		<label class="jf-choice"><input type="radio" name="time_mode" value="unknown"><span>I don't know</span></label>
	</div>
	<label class="jade-field" data-when="exact"><span>Birth time</span><input type="time" name="birth_time" step="60"></label>
	<label class="jade-field" data-when="rough" hidden><span>Roughly when were you born?</span>
		<select name="rough_time">
			<option value="04:30">Early morning (3 – 6 am)</option>
			<option value="08:00">Morning (6 – 10 am)</option>
			<option value="12:00" selected>Midday (10 am – 2 pm)</option>
			<option value="16:00">Afternoon (2 – 6 pm)</option>
			<option value="20:00">Evening (6 – 10 pm)</option>
			<option value="23:30">Late night (10 pm – 1 am)</option>
		</select>
	</label>
	<p class="jade-small jade-muted" data-when="exact">It's on most birth certificates. The exact minute adds your rising sign and more rarity checks.</p>
	<p class="jade-small jade-muted" data-when="unknown" hidden>No problem. We'll read everything that doesn't depend on the minute, using your Moon as the starting point, a traditional Vedic method.</p>
	<div class="jf-nav"><button type="button" class="jade-link" data-back>Back</button><button type="button" class="jade-btn" data-next>Next</button></div>
</fieldset>
<fieldset class="jf-step" data-step="focus" hidden>
	<legend>What's on your mind most right now?</legend>
	<p class="jade-small jade-muted">Pick as many as you like. Your reading starts with these.</p>
	<div class="jf-choices jf-topics">
		<label class="jf-choice"><input type="checkbox" name="topics" value="love"{tchk('love')}><span>Love &amp; relationships</span></label>
		<label class="jf-choice"><input type="checkbox" name="topics" value="career"{tchk('career')}><span>Career</span></label>
		<label class="jf-choice"><input type="checkbox" name="topics" value="money"{tchk('money')}><span>Money</span></label>
		<label class="jf-choice"><input type="checkbox" name="topics" value="health"><span>Energy &amp; wellbeing</span></label>
		<label class="jf-choice jf-choice--year"><input type="checkbox" name="topics" value="year"><span>My next 12 months<small>Know when to push and when to wait. The next 12 months decide a lot.</small></span></label>
	</div>
	<div class="jf-nav"><button type="button" class="jade-link" data-back>Back</button><button type="button" class="jade-btn" data-next>Next</button></div>
</fieldset>
<fieldset class="jf-step" data-step="you" hidden>
	<legend>Last step</legend>
	<div class="jf-row2">
		<label class="jade-field"><span>First name</span><input type="text" name="first_name" autocomplete="given-name" maxlength="60" required placeholder="So your reading can use it"></label>
		<label class="jade-field"><span>Last name <em class="jade-muted">(optional)</em></span><input type="text" name="last_name" autocomplete="family-name" maxlength="60"></label>
	</div>
	<p class="jf-label">I am</p>
	<div class="jf-choices jf-choices--3" role="radiogroup">
		<label class="jf-choice"><input type="radio" name="gender" value="female"><span>Female</span></label>
		<label class="jf-choice"><input type="radio" name="gender" value="male"><span>Male</span></label>
		<label class="jf-choice"><input type="radio" name="gender" value="unspecified" checked><span>Rather not say</span></label>
	</div>
	<p class="jf-label">Read my chart in</p>
	<div class="jf-choices jf-choices--trad" role="radiogroup">
		<label class="jf-choice jf-choice--main"><input type="radio" name="tradition" value="vedic" checked><span><strong>Vedic</strong> <em>Recommended</em><small>The deeper reading: your birth star, your life chapters and their exact timing.</small></span></label>
		<label class="jf-choice jf-choice--alt"><input type="radio" name="tradition" value="western"><span><strong>Western</strong><small>Sun, Moon and Rising only.</small></span></label>
	</div>
	<div class="jade-hp" aria-hidden="true"><label>Website <input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
	<div class="jf-nav"><button type="button" class="jade-link" data-back>Back</button><button type="submit" class="jade-btn jade-btn--gold">{e(button)}</button></div>
</fieldset>
<p class="jade-error" role="alert" hidden></p>
</form>
<div class="jf-calc" hidden aria-live="polite">
	<div class="jf-orbit" aria-hidden="true"><span></span></div>
	<ul>
		<li>Placing the planets for your birth minute</li>
		<li>Finding your birth star among the 27 Nakshatras</li>
		<li>Checking the classical yogas in your chart</li>
		<li>Measuring how rare your chart is</li>
	</ul>
</div>
</div>
<div class="jf-result"></div>
</section>"""

    def place_field(self, uid, name="birth_place", label="City of birth", prefix=""):
        """City search with suggestions, plus the optional exact-spot map."""
        return f"""<div class="jade-field jade-place">
		<label for="{uid}-{prefix}place">{e(label)}</label>
		<input type="text" id="{uid}-{prefix}place" name="{prefix}{name}" maxlength="200" placeholder="Start typing the city" autocomplete="off"
			role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="{uid}-{prefix}list">
		<ul class="jade-place__list" id="{uid}-{prefix}list" role="listbox" hidden></ul>
		<input type="hidden" name="{prefix}place_id" value="">
		<input type="hidden" name="{prefix}place_session" value="">
		<input type="hidden" name="{prefix}lat" value="">
		<input type="hidden" name="{prefix}lng" value="">
	</div>
	<div class="jade-exact" data-jade-exact data-prefix="{prefix}">
		<button type="button" class="jade-link" data-exact-open>Advanced search: pin the exact place of birth</button>
		<div class="jade-exact__panel" hidden>
			<p class="jade-small">The exact spot makes your chart more precise. Your rising sign and houses move with every few miles, so pinning the house or hospital you were born in sharpens every prediction.</p>
			<input type="text" class="jade-exact__search" placeholder="Search the address or hospital" aria-label="Search the address or hospital">
			<div class="jade-exact__map" role="application" aria-label="Map: tap the exact place you were born"></div>
			<p class="jade-small jade-muted" data-exact-status>Search, then tap or drag the pin onto the exact building.</p>
			<div class="jf-nav"><button type="button" class="jade-link" data-exact-cancel>Cancel</button><button type="button" class="jade-btn" data-exact-use>Use this spot</button></div>
		</div>
	</div>"""

    # ------------------------------------------------------------------ horoscopes
    def horo_data(self, period, sign):
        block = self.h.get(period) or {}
        return block, (block.get("signs") or {}).get(sign)

    def period_label(self, period):
        block = self.h.get(period) or {}
        if period == "weekly":
            return block.get("label") or "This week"
        if period == "monthly":
            return block.get("label") or self.now.strftime("%B %Y")
        try:
            d = dt.date.fromisoformat(block.get("date", ""))
            return d.strftime("%A, %B %-d, %Y")
        except ValueError:
            day = self.now + (dt.timedelta(days=1) if period == "tomorrow" else dt.timedelta())
            return day.strftime("%A, %B %-d, %Y")

    def horoscope(self, sign, period="daily", only=None):
        block, data = self.horo_data(period, sign)
        if not data:
            what = {"weekly": "weekly", "monthly": "monthly", "tomorrow": "tomorrow"}.get(period, "daily")
            return (f'<section class="jade-horoscope"><p class="jade-notice">{e(self.sname(sign))}\'s {what} horoscope '
                    "is being prepared. Please check back in a few minutes.</p></section>")
        out = f'<section class="jade-horoscope"><p class="jade-date">{e(self.period_label(period))}</p>'
        if block.get("sample"):
            out += '<p class="jade-notice jade-small">Sample text. The real horoscope appears here once the site is connected.</p>'
        pct = data.get("percentages") or {}
        for key, label in SECTION_LABELS:
            if only and key not in only:
                continue
            txt = (data.get("sections") or {}).get(key)
            if not isinstance(txt, str) or not txt:
                continue
            out += f'<div class="jade-section"><div class="jade-section__head"><h3>{e(label)}</h3>'
            if key in pct:
                v = max(0, min(100, int(pct[key])))
                out += (f'<span class="jade-meter" role="img" aria-label="{e(label)} energy {v}%"><span style="width:{v}%"></span></span>'
                        f'<span class="jade-meter__num">{v}%</span>')
            out += f"</div><p>{e(txt)}</p></div>"
        luck = (data.get("sections") or {}).get("luck")
        if not only and isinstance(luck, list) and luck:
            out += '<div class="jade-luck"><h3>Luck &amp; tips</h3><dl>'
            for line in luck:
                parts = [p.strip() for p in str(line).split(":", 1)]
                out += (f"<div><dt>{e(parts[0])}</dt><dd>{e(parts[1])}</dd></div>" if len(parts) == 2
                        else f"<div><dd>{e(line)}</dd></div>")
            out += "</dl></div>"
        return out + "</section>"

    def folded(self, inner, sign, when):
        what = {"this week": "weekly horoscope", "this month": "monthly horoscope", "tomorrow": "horoscope for tomorrow"}.get(when, "horoscope for today")
        n = self.sname(sign)
        return (f'<details class="jade-generic" id="jade-horo"><summary>Read the general {e(n)} {what} '
                f'(the same for every {e(n)})</summary>{inner}</details>')

    def sign_grid(self, kind="daily"):
        out = '<nav class="jade-grid" aria-label="Zodiac signs">'
        for s in SIGNS:
            href = {"daily": f"/{s}-horoscope-today/", "weekly": f"/{s}-weekly-horoscope/",
                    "monthly": f"/{s}-monthly-horoscope/",
                    "compat": f"/{s}-compatibility/"}[kind]
            out += (f'<a class="jade-grid__item" href="{href}"><span class="jade-grid__glyph" aria-hidden="true">'
                    f'{e(self.symbol(s))}</span><span class="jade-grid__name">{e(self.sname(s))}</span>'
                    f'<span class="jade-grid__dates">{e(self.signs[s]["dates"])}</span></a>')
        return out + "</nav>"

    def chips(self, items, label):
        return (f'<nav class="jade-chips" aria-label="{e(label)}">' +
                "".join(f'<a href="{e(h)}">{e(t)}</a>' for h, t in items) + "</nav>")

    def sign_links(self, suffix, label):
        return self.chips([(f"/{s}-{suffix}/", self.sname(s)) for s in SIGNS], f"Other signs: {label}")

    def nak_links(self):
        return "<h2>All 27 Nakshatras</h2>" + self.chips(
            [(f"/nakshatra/{slug}/", n["name"]) for slug, n in self.naks.items()], "Nakshatras")

    # ------------------------------------------------------------------ sample content (test mode / first boot)
    def sample_horoscopes(self):
        def one(s):
            n = self.signs[s]["name"]
            return {"sections": {
                "personal": f"Sample text for {n}. The real daily horoscope is written each morning from the actual sky.",
                "emotions": "Sample text. Emotions section.", "profession": "Sample text. Career section.",
                "health": "Sample text. Health and wellbeing section.", "travel": "Sample text. Travel section.",
                "luck": ["Lucky color: jade green", "Lucky number: 7", "Tip: sample tip"]},
                "percentages": {"personal": 70, "emotions": 60, "profession": 80, "health": 65, "travel": 50}}
        d = self.now.date()
        return {"daily": {"date": d.isoformat(), "sample": True, "signs": {s: one(s) for s in SIGNS}},
                "tomorrow": {"date": (d + dt.timedelta(days=1)).isoformat(), "sample": True, "signs": {s: one(s) for s in SIGNS}},
                "weekly": {"label": "Week of " + self.week_start().strftime("%B %-d"), "sample": True, "signs": {s: one(s) for s in SIGNS}},
                "monthly": {"label": self.now.strftime("%B %Y"), "sample": True, "signs": {s: one(s) for s in SIGNS}}}

    def sample_compat(self):
        pairs = {}
        for i, a in enumerate(SIGNS):
            for b in SIGNS[i:]:
                pairs[f"{a}-{b}"] = {"sample": True, "score": 70,
                                     "summary": f"Sample text for {self.sname(a)} and {self.sname(b)}.",
                                     "love": "Sample text: love and chemistry.", "communication": "Sample text: communication.",
                                     "challenges": "Sample text: where you clash.", "long_term": "Sample text: the long run."}
        signs = {s: {"sample": True, "compatibility": f"Sample text: who {self.sname(s)} gets on with.",
                     "soulmate": f"Sample text: the {self.sname(s)} soulmate.",
                     "best": [SIGNS[(SIGNS.index(s) + k) % 12] for k in (4, 8, 6)]} for s in SIGNS}
        return {"pairs": pairs, "signs": signs}

    # ------------------------------------------------------------------ build
    def build_all(self):
        from pages_content import build_pages  # the page bodies
        build_pages(self)
        self.files["404.html"] = self.layout("404", f"Page not found | {BRAND}", "", (
            '<div class="not-found"><h1>That page isn\'t here</h1><p>It may have moved. '
            'Try <a href="/horoscope-today/">today\'s horoscope</a> or a <a href="/free-reading/">free reading</a>.</p></div>'),
            True, "")
        self.files["robots.txt"] = f"User-agent: *\nDisallow: /checkout/\nDisallow: /thank-you/\nDisallow: /partner/\n\nSitemap: {self.url()}sitemap.xml\n"
        today = self.now.date().isoformat()
        urls = "".join(f"<url><loc>{e(self.url(s))}</loc><lastmod>{today}</lastmod></url>" for s in self.sitemap)
        self.files["sitemap.xml"] = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                                     f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
        return self.files
