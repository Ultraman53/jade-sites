"""Page bodies for every address on the site."""
from pages import (SIGNS, YEAR, BRAND, COMPANY, ADDRESS, EMAIL, e, ordinal, pair_key, pair_slug)

# --- Landing pages (same addresses and wording as the live site) -----------------------------
# slug: (template, h1, meta description, topic, focus, intent)
STATICS = {
    "birth-chart-calculator": ("A", "Free Birth Chart Calculator", "Free birth chart calculator: your Vedic and Western chart, birth star and how rare your chart is, from your exact birth time and place.", "chart"),
    "rising-sign-calculator": ("A", "Rising Sign Calculator", "Find your rising sign (ascendant) free from your birth time and place, in both Western and Vedic astrology.", "rising"),
    "moon-sign-calculator": ("A", "Moon Sign Calculator", "Calculate your Moon sign free from your birth date, time and place, with your Vedic birth star (Nakshatra).", "moon"),
    "big-three-calculator": ("A", "Big Three Calculator: Sun, Moon and Rising", "Find your Sun, Moon and Rising signs free, calculated from your exact birth chart.", "big3"),
    "nakshatra-calculator": ("D", "Nakshatra Calculator: Find Your Birth Star", "Find your Nakshatra (Vedic birth star) and pada free, with what it says about you.", "nakshatra"),
    "free-birth-chart": ("C", "Your Free Birth Chart, Read for You", "Get your free birth chart reading: placements, birth star, life chapters and how rare your chart is.", "chart"),
    "horoscope-by-date-of-birth": ("C", "Horoscope by Date of Birth", "Your personal horoscope by date of birth, calculated from your own chart instead of your Sun sign.", "day"),
    "birth-chart-reading": ("C", "Free Birth Chart Reading", "A free, personal birth chart reading in plain English, with your rarest placements explained.", "chart"),
    "vedic-birth-chart": ("D", "Free Vedic Birth Chart", "Free Vedic birth chart (Jyotish): lagna, Moon sign, Nakshatra, yogas and your Vimshottari dasha timeline.", "chart"),
    "kundli-online": ("D", "Free Kundli Online, in English", "Make your kundli (janam kundali) online free in English, with your Nakshatra, yogas and dasha explained.", "chart"),
    "vedic-astrology-reading": ("D", "Free Vedic Astrology Reading", "A free Vedic astrology reading from your birth chart, with your birth star and life timeline.", "chart"),
    "when-will-i-get-married": ("E", "When Will I Get Married? What Your Chart Says", "See what your birth chart says about marriage and timing: your 7th house, its ruler and your coming periods.", "marriage"),
    "future-spouse-astrology": ("E", "Your Future Spouse in Astrology", "What your birth chart says about your future spouse: your 7th house, its ruler and Venus.", "marriage"),
    "love-horoscope": ("E", "Love Horoscope, From Your Own Chart", "A love horoscope from your own birth chart: your 7th house, Venus and your next turning point.", "love"),
    "career-astrology": ("F", "Career Astrology: What Your Chart Says About Work", "Career astrology from your birth chart: your 10th house, its ruler and the periods that drive your work.", "career"),
    "money-horoscope": ("F", "Money Horoscope, From Your Own Chart", "Your money horoscope from your birth chart: wealth houses, their rulers and your timing.", "money"),
    "saturn-return-calculator": ("H", "Saturn Return Calculator", "Find your Saturn return dates free from your birth chart, and what Saturn means for you.", "saturn"),
    f"{YEAR}-horoscope": ("H", f"Your {YEAR} Horoscope, From Your Own Chart", f"Your {YEAR} horoscope from your own birth chart: the planetary periods you live through in {YEAR}.", "year"),
}

HOUSES = {1: "self and identity", 2: "money and values", 3: "communication and siblings", 4: "home and family",
          5: "romance and creativity", 6: "work and health", 7: "partnership and marriage", 8: "shared resources and change",
          9: "luck, travel and beliefs", 10: "career and reputation", 11: "friends and gains", 12: "rest and the hidden"}


def static_body(site, tpl):
    out = ('<h2>What you get, free</h2><ul class="jade-ticks">'
           "<li>How rare your chart is, with the placements that make it rare and the math</li>"
           "<li>Your Sun, Moon and Rising in both Vedic and Western astrology</li>"
           "<li>Your birth star (Nakshatra) and what it says about you</li>"
           "<li>Your life chapters (dashas): the one you just left, the one you are in, and your next turning point</li>"
           "<li>What your chart says about love, career and money</li></ul>"
           "<h2>How it works</h2><p>We calculate the exact positions of the planets for the minute and place you were born, "
           "using the same astronomical methods professional astrologers use. Then we read the chart for you: every term "
           "explained in plain English, every claim tied to a placement in your own chart. No email is needed to see your reading.</p>")
    if tpl == "D":
        out += site.nak_links()
    return out


def year_text(site, sign):
    i = SIGNS.index(sign)
    h = lambda ps: (SIGNS.index(ps) - i + 12) % 12 + 1  # noqa: E731
    n = site.sname(sign)
    sat, j1, j2 = h("aries"), h("leo"), h("virgo")
    return [
        f"Saturn spends all of {YEAR} in Aries, your {ordinal(sat)} house of {HOUSES[sat]} (counting from {n}). Saturn is the planet of work, time and commitment, so this is the area of life where {YEAR} asks for patience and effort, and where that effort lasts.",
        f"Jupiter, the planet of growth and luck, is in Leo, your {ordinal(j1)} house of {HOUSES[j1]}, until late July {YEAR}. It then moves into Virgo, your {ordinal(j2)} house of {HOUSES[j2]}, for the rest of the year. Those are the areas where doors tend to open.",
        f"This is the Sun sign view, which every {n} shares. Your own chart decides where these planets actually land for you, and which life chapter you are in while they do. Calculate yours below.",
    ]


def route_page(site, slug, h1, desc, body_html, funnel_html, title=None, pagehead=None):
    inner = f'<div class="jade jade-wrap">'
    if pagehead:
        inner += pagehead
    inner += funnel_html + f'<div class="jade-route-body">{body_html}</div></div>'
    site.add(slug, title or f"{h1} | {BRAND}", desc, inner)


# --- Compatibility -------------------------------------------------------------------------------
def person_fields(site, uid, who, prefix, label):
    months = "".join(f'<option value="{i + 1}">{m}</option>' for i, m in enumerate(
        ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]))
    days = "".join(f'<option value="{d}">{d}</option>' for d in range(1, 32))
    years = "".join(f'<option value="{y}">{y}</option>' for y in range(site.now.year, 1919, -1))
    return f"""<fieldset class="jc-person" data-person="{prefix}">
	<legend>{e(label)}</legend>
	<label class="jade-field"><span>First name</span><input type="text" name="{prefix}name" maxlength="60" required></label>
	<div class="jf-row3">
		<label class="jade-field"><span>Month</span><select name="{prefix}b_month" required><option value="">Month</option>{months}</select></label>
		<label class="jade-field"><span>Day</span><select name="{prefix}b_day" required><option value="">Day</option>{days}</select></label>
		<label class="jade-field"><span>Year</span><select name="{prefix}b_year" required><option value="">Year</option>{years}</select></label>
	</div>
	<label class="jade-field"><span>Birth time</span><input type="time" name="{prefix}birth_time" step="60"></label>
	<label class="jade-check"><input type="checkbox" name="{prefix}time_unknown" value="1"> <span>{"I" if who == "you" else "They"} don't know the birth time</span></label>
	{site.place_field(uid, prefix=prefix, label="City of birth")}
</fieldset>"""


def compat_widget(site, intent, head, sub, tag="h1", a="", b=""):
    uid = f"jc-{intent}"
    pre = f' data-sign-a="{e(a)}" data-sign-b="{e(b)}"' if a else ""
    return f"""<section class="jade-funnel jade-compat" data-jade-compat data-intent="{e(intent)}"{pre}>
<div class="jf-head"><p class="jade-eyebrow">Free · from both birth charts · no email needed</p>
<{tag} class="jf-title">{e(head)}</{tag}><p class="jf-sub">{e(sub)}</p></div>
<div class="jf-box">
<form class="jc-form" novalidate>
<div class="jc-people">
{person_fields(site, uid, "you", "a_", "You")}
{person_fields(site, uid, "them", "b_", "Them")}
</div>
<label class="jade-check"><input type="checkbox" name="partner_ok" value="1"> <span>I have their permission to use their birth details.</span></label>
<p class="jade-small jade-muted">Birth details are used only to calculate the match. We never share them.</p>
<div class="jade-hp" aria-hidden="true"><label>Website <input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
<p class="jade-error" role="alert" hidden></p>
<div class="jf-nav"><button type="submit" class="jade-btn jade-btn--gold">Show our match →</button></div>
</form>
<div class="jf-calc" hidden aria-live="polite"><div class="jf-orbit" aria-hidden="true"><span></span></div>
<ul><li>Placing both charts</li><li>Matching your Moons and birth stars (the 36-point Guna match)</li><li>Comparing Venus, Mars and your 7th houses</li></ul></div>
</div>
<div class="jf-result"></div>
</section>"""


def compat_text(site, a, b):
    k = "-".join(pair_key(a, b))
    return (site.c.get("pairs") or {}).get(k) or {}


def build_compat(site):
    head_sub = "Enter both birth dates, times and places. A real chart-to-chart match, not a name game."
    site.add("compatibility-calculator", f"Compatibility Calculator: Birth Chart Match | {BRAND}",
             "Free compatibility calculator from both birth charts: the 36-point Vedic Guna match plus Venus, Mars and Moon synastry.",
             '<div class="jade jade-wrap">' + compat_widget(site, "compat", "Compatibility Calculator", head_sub) +
             '<div class="jade-route-body"><h2>How we match two charts</h2><p>Sun signs are only the start. We calculate both full birth charts and compare them the way astrologers do: the Vedic 36-point Guna match between your Moons and birth stars, then how your Venus, Mars and Moon meet each other, and whether your 7th houses (the house of partnership) support the bond.</p>'
             '<h2>Zodiac compatibility by sign</h2>' + site.sign_grid("compat") + '</div></div>')
    site.add("love-calculator", f"Love Calculator: Real Birth Chart Compatibility | {BRAND}",
             "A love calculator built on astrology, not names: enter both birth dates to see your chemistry, your clashes and your match score.",
             '<div class="jade jade-wrap">' + compat_widget(site, "love", "Love Calculator", "Not a name game: your real love match from both birth charts. Chemistry, clashes and your score.") +
             '<div class="jade-route-body"><h2>Why birth dates beat names</h2><p>Name-based love calculators are a coin toss. Your birth charts show how each of you loves, what each of you needs, and where you rub against each other. Enter both birth dates (and times, if you know them) for the real answer.</p>' + site.sign_grid("compat") + '</div></div>')
    site.add("synastry-calculator", f"Synastry Calculator: Compare Two Birth Charts | {BRAND}",
             "Free synastry calculator: compare two birth charts, planet to planet, with the Vedic Guna match and plain-English meaning.",
             '<div class="jade jade-wrap">' + compat_widget(site, "synastry", "Synastry Calculator", "Compare two birth charts planet to planet, plus the Vedic 36-point match.") +
             '<div class="jade-route-body"><h2>What synastry shows</h2><p>Synastry lays one birth chart over another. Where one person\'s planets fall in the other\'s chart shows attraction, comfort, friction and growth. We explain every connection in plain English.</p></div></div>')

    hub = '<div class="jade jade-wrap"><header class="jade-pagehead"><h1>Zodiac Compatibility</h1></header><p class="jade-intro">Pick your sign for every match, or jump to a pair below. For the real answer, compare your two birth charts in the <a href="/compatibility-calculator/">compatibility calculator</a>.</p>' + site.sign_grid("compat")
    hub += "<h2>Every pair</h2>"
    items = []
    for i, a in enumerate(SIGNS):
        for b in SIGNS[i:]:
            items.append((f"/{pair_slug(a, b)}/", f"{site.sname(a)} & {site.sname(b)}"))
    hub += site.chips(items, "All sign pairs") + "</div>"
    site.add("zodiac-compatibility", f"Zodiac Compatibility: Every Sign Pair | {BRAND}",
             "Zodiac compatibility for every sign pair: love, communication, clashes and the long run, plus a free birth chart match.", hub)

    for i, a in enumerate(SIGNS):
        for b in SIGNS[i:]:
            na, nb = site.sname(a), site.sname(b)
            t = compat_text(site, a, b)
            title = f"{na} and {nb} Compatibility" if a != b else f"{na} and {na} Compatibility"
            body = ""
            if t.get("sample"):
                body += '<p class="jade-notice jade-small">Sample text. The real text appears here once the site is connected.</p>'
            if t.get("summary"):
                body += f'<p class="jade-intro">{e(t["summary"])}</p>'
            for key, label in (("love", "Love and chemistry"), ("communication", "How you talk and argue"),
                               ("challenges", "Where you clash"), ("long_term", "The long run")):
                if t.get(key):
                    body += f"<h2>{e(label)}</h2><p>{e(t[key])}</p>"
            body += (f"<h2>Your Sun signs are only the start</h2><p>Two {na}s and two {nb}s can have very different "
                     "relationships. The real match is in your Moons, your Venus and Mars, and your 7th houses. "
                     "Compare your actual birth charts above.</p>")
            body += f"<h2>More {e(na)} matches</h2>" + site.chips(
                [(f"/{pair_slug(a, x)}/", f"{na} & {site.sname(x)}") for x in SIGNS], f"{na} matches")
            widget = compat_widget(site, "compat", title, f"Check the real {na}–{nb} match from both birth charts. Free, no email needed.", "h1", a, b)
            site.add(pair_slug(a, b), f"{title}: Love, Friendship and Your Real Match | {BRAND}",
                     f"{na} and {nb} compatibility in love and friendship: chemistry, communication, clashes and the long run, plus your real birth chart match.",
                     f'<div class="jade jade-wrap">{widget}<div class="jade-route-body">{body}</div></div>')

    for s in SIGNS:
        n = site.sname(s)
        t = (site.c.get("signs") or {}).get(s) or {}
        sample = '<p class="jade-notice jade-small">Sample text. The real text appears here once the site is connected.</p>' if t.get("sample") else ""
        best = t.get("best") or []
        best_html = ("<h2>Best matches</h2>" + site.chips([(f"/{pair_slug(s, x)}/", f"{n} & {site.sname(x)}") for x in best if x in SIGNS], "Best matches")) if best else ""
        allm = f"<h2>{e(n)} with every sign</h2>" + site.chips([(f"/{pair_slug(s, x)}/", site.sname(x)) for x in SIGNS], "Every match")
        site.add(f"{s}-compatibility", f"{n} Compatibility: Best and Worst Matches | {BRAND}",
                 f"{n} compatibility with every sign: best matches, hardest matches, and how to check your real match from both birth charts.",
                 '<div class="jade jade-wrap">' + compat_widget(site, "compat", f"{n} Compatibility", f"Your Sun sign is one piece. Check your real match from both birth charts.", "h1", s) +
                 f'<div class="jade-route-body">{sample}<p class="jade-intro">{e(t.get("compatibility", ""))}</p>{best_html}{allm}</div></div>')
        site.add(f"{s}-soulmate", f"{n} Soulmate: Who Is the {n}'s Perfect Match? | {BRAND}",
                 f"Who is the {n} soulmate? The signs that fit {n} best, and how your 7th house shows the partner you are really built for.",
                 '<div class="jade jade-wrap">' + site.funnel("love", head=f"{n} Soulmate", tag="h1", sign=s, source=f"{s}-soulmate") +
                 f'<div class="jade-route-body">{sample}<h2>The {e(n)} soulmate</h2><p>{e(t.get("soulmate", ""))}</p>{best_html}'
                 "<h2>Your 7th house knows more</h2><p>In Vedic astrology the partner you are built for is described by your 7th house and its ruling planet, not by your Sun sign. Enter your birth details above to read yours.</p></div></div>")


# --- Info, legal and order pages -----------------------------------------------------------------
def legal(site):
    o = site.offers
    pct, days, desc = o["refund_percent"], o["refund_days"], o["statement_descriptor"]
    updated = f"Last updated: {site.now.strftime('%B %-d, %Y')}"
    mail = f'<a href="mailto:{EMAIL}">{EMAIL}</a>'
    pages = {
        "about": ("About Us", f"""<p>{BRAND} publishes daily, weekly and monthly horoscopes for all twelve zodiac signs, free calculators, and personal readings based on your own birth chart.</p>
<h2>How our readings are made</h2>
<p>Your chart is calculated from astronomical data for the exact date, time and place you provide, in both the Vedic (sidereal) and Western (tropical) systems. Free readings and daily horoscopes are calculated and written automatically by our software. Paid reports are prepared and reviewed by our astrologer before they are sent, and nothing is sent without that review.</p>
<h2>How we calculate rarity</h2>
<p>When we say a chart is "about 1 in 52,000", we take the rarest placements in your chart that depend on different parts of the sky (for example, a planet in its sign of exaltation, which happens in about 1 in 12 births), multiply their simple odds together, and round. We use conservative odds and count at most three placements.</p>
<h2>Who we are</h2>
<p>{BRAND} is a brand of {COMPANY}, {e(ADDRESS)}.</p>
<p>Questions or feedback? Write to us at {mail}.</p>
<p><em>Astrology is offered for personal guidance and self-reflection. Please don't rely on it for medical, legal, financial or other important decisions.</em></p>"""),
        "contact": ("Contact", f"""<p>We'd love to hear from you.</p>
<p><strong>Email:</strong> {mail}<br><strong>Mail:</strong> {COMPANY}, {e(ADDRESS)}</p>
<p>We usually reply within two business days. To stop receiving our emails, use the unsubscribe link at the bottom of any email; it takes effect immediately.</p>
<p>Need a refund? Use our <a href="/refund-request/">refund request form</a>.</p>"""),
        "privacy-policy": ("Privacy Policy", f"""<p><em>{updated}</em></p>
<p>This policy explains how {COMPANY} ("we", "us") collects and uses personal information on the {BRAND} website and in our emails.</p>
<h2>What we collect</h2>
<ul>
<li><strong>Information you give us:</strong> your email address and, if you request a reading, your first name, optional last name, gender (or "rather not say"), the topics you choose, and your date, time and place of birth, including an exact location if you pin one on the map.</li>
<li><strong>Information collected automatically:</strong> basic technical data such as browser type, pages visited and the advertising campaign or search that brought you here.</li>
<li><strong>If you buy a report:</strong> your email for delivery, and a record that you agreed to our terms and refund policy: the time, your IP address, your browser and device details, and the exact wording you agreed to. We keep this with your order as proof of purchase. Payment card details are handled by Whop and never reach us.</li>
<li><strong>If you buy a compatibility reading:</strong> your partner's first name and birth details, which you confirm you have their permission to share.</li>
<li><strong>Cookies and similar technologies:</strong> we and our advertising and analytics partners (such as Google) may use cookies to measure visits and ad performance.</li>
</ul>
<h2>How we use it</h2>
<ul>
<li>To calculate your chart and readings, to deliver what you bought, and, if you agreed, to email you about your reading with personal insights from your chart and offers from us.</li>
<li>To run, secure and improve the website and measure our advertising.</li>
</ul>
<h2>Who we share it with</h2>
<p>We do not sell your personal information. We share it only with service providers that help us run {BRAND}, under their own privacy and security commitments: website hosting and security (DigitalOcean, Cloudflare), our order, reading and email systems (Amazon Web Services), payments (Whop), writing parts of readings and horoscopes (Anthropic, which receives calculated chart positions), birthplace search and maps (Google), and analytics and advertising (Google). We may disclose information if required by law.</p>
<h2>How long we keep it</h2>
<p>We keep your information while you are subscribed or a customer and for a reasonable period afterwards for record-keeping, then delete it. You can ask us to delete it at any time.</p>
<h2>Your choices and rights</h2>
<ul>
<li><strong>Unsubscribe</strong> from any email using the link at the bottom; it takes effect immediately.</li>
<li><strong>Access, correct or delete</strong> your information by emailing {mail}. Depending on where you live (for example, California and other US states), you may have additional rights, and we will honor them.</li>
</ul>
<h2>Children</h2>
<p>{BRAND} is intended for adults aged 18 and over. We do not knowingly collect information from anyone under 18.</p>
<h2>Security</h2>
<p>We use reasonable technical measures to protect your information, but no system is completely secure.</p>
<h2>Changes and contact</h2>
<p>We may update this policy and will change the date above when we do. Questions: {mail} or {COMPANY}, {e(ADDRESS)}.</p>"""),
        "terms": ("Terms of Use", f"""<p><em>{updated}</em></p>
<p>These terms govern your use of the {BRAND} website and emails, operated by {COMPANY}, {e(ADDRESS)}. By using the site you agree to them.</p>
<h2>About our readings</h2>
<p>Horoscopes, readings and reports are calculated from astronomical data using traditional Vedic and Western astrological methods and are offered for personal guidance and self-reflection. Astrology is an interpretive tradition, not a science; our readings are not guarantees of future events and are not a substitute for professional medical, legal, financial, psychological or other advice.</p>
<h2>Paid reports</h2>
<p>Reports are personalized digital products, prepared from the birth details you provide, reviewed by our astrologer and delivered {e(o["delivery"])}. Please check your birth details before you buy. Prices are shown before checkout in US dollars. Payment is processed by Whop, and the charge appears on your card statement as <strong>{desc}</strong>. Refunds are covered by our <a href="/refund-policy/">Refund Policy</a>: refunds are {pct}% of the price, and redos are always free.</p>
<h2>Eligibility</h2>
<p>You must be at least 18 years old to buy reports and use our personal reading and email services. Paid reports are available to customers in the United States only.</p>
<h2>Your information</h2>
<p>You agree to provide accurate information. Our use of your information is described in our <a href="/privacy-policy/">Privacy Policy</a>.</p>
<h2>Intellectual property</h2>
<p>The content and design of this site belong to {COMPANY} or its licensors. You may read and share links to it for personal, non-commercial use.</p>
<h2>No warranties; limitation of liability</h2>
<p>The site is provided "as is" without warranties of any kind. To the fullest extent permitted by law, {COMPANY} is not liable for any indirect or consequential damages arising from your use of the site or reliance on its content.</p>
<h2>Governing law</h2>
<p>These terms are governed by the laws of the Commonwealth of Kentucky, USA.</p>
<h2>Contact</h2>
<p>{mail}</p>"""),
        "refund-policy": ("Refund Policy", f"""<p><em>{updated}</em></p>
<p>We will only refund {pct}% of what you paid, because it takes a real astrologer's time and effort to create your reading. The {100 - pct}% we keep still doesn't cover the expense of that time and expertise, but it makes the work somewhat worthwhile. Redos, however, cost nothing.</p>
<h2>How to request a refund</h2>
<p>Use our <a href="/refund-request/">refund request form</a>, or email {mail} within {days} days of receiving your reading, and tell us what we got wrong. Your feedback helps us get better.</p>
<h2>When you'll get it</h2>
<p>We process refunds immediately. Your bank may take 5–10 business days to show it on your original payment method.</p>
<h2>Before we start</h2>
<p>If you cancel before we've begun your reading, you get 100% back.</p>
<h2>Free redos</h2>
<p>If anything in your reading is wrong, unclear, or doesn't feel like you, or you entered the wrong birth details, tell us within {days} days and we'll redo it free, as many times as it takes. We'd rather fix it than refund it.</p>
<h2>Add-ons</h2>
<p>Compatibility readings, forecasts and custom questions follow the same policy.</p>
<h2>On your card statement</h2>
<p>Your purchase appears as <strong>{desc}</strong>.</p>
<p>{BRAND} is a brand of {COMPANY}, {e(ADDRESS)}.</p>"""),
        "disclaimer": ("Disclaimer", f"""<p>The horoscopes, readings and other content on {BRAND} are calculated from astronomical data using traditional Vedic and Western methods and are intended for personal guidance and self-reflection.</p>
<p>They are not scientific predictions and should not be used as the basis for decisions about your health, relationships, finances, career or legal matters. Always seek the advice of a qualified professional for those.</p>
<p>If you are struggling or in crisis, please contact a medical professional or, in the US, call or text 988 for the Suicide &amp; Crisis Lifeline.</p>"""),
    }
    for slug, (h1, body) in pages.items():
        site.add(slug, f"{h1} | {BRAND}", "", f'<article class="entry"><h1 class="entry-title">{e(h1)}</h1><div class="entry-content">{body}</div></article>')

    # Pricing
    pages_line = f"Full {o['report_pages']}-page report. " if o.get("report_pages") else ""
    body = f"""<h2>{e(o['main']['name'])} — ${o['main']['price']}</h2>
<p><strong>One-time payment.</strong> {pages_line}A personalized, in-depth written reading of your Vedic birth chart: your strengths, personality, relationships, career, money and life timing, prepared and reviewed by our astrologer. Delivered {e(o['delivery'])}.</p>
<h2>{e(o['bump']['name'])} — ${o['bump']['price']}</h2>
<p><strong>Optional add-on.</strong> What each of the next 12 months holds for you, starting from your purchase date.</p>
<h2>{e(o['compat']['name'])} — ${o['compat']['price']}</h2>
<p><strong>Optional add-on.</strong> How your chart and your partner's chart work together. {e(o['compat']['bonus'])}.</p>
<p>All prices in USD. One-time payments, no subscriptions. Available to customers in the United States only. Your card statement shows <strong>{e(o['statement_descriptor'])}</strong>.</p>
<p>Refunds are {pct}% of the price because every reading takes our astrologer's time and expertise; redos are always free. See our <a href="/refund-policy/">Refund Policy</a>.</p>
<p>Questions? Email {mail}.</p>"""
    site.add("pricing", f"Pricing | {BRAND}", "Jade Astrology pricing: personal Vedic reports and add-ons, one-time payments in USD.",
             f'<article class="entry"><h1 class="entry-title">Pricing</h1><div class="entry-content">{body}</div></article>')


def order_pages(site):
    o = site.offers
    pct = o["refund_percent"]
    # Checkout: the box, its 80% line and the statement note are part of the page, never hidden behind a link.
    checkout = f"""<div class="jade jade-wrap jade-checkout" data-jade-checkout>
<header class="jade-pagehead"><p class="jade-eyebrow">Secure checkout</p><h1>Your order</h1></header>
<div class="jade-co" data-co-loading><p class="jade-muted">Loading your order…</p></div>
<form class="jade-co__form" novalidate hidden>
	<ul class="jade-co__lines" data-co-lines></ul>
	<label class="jade-co__bump" data-co-bump hidden><input type="checkbox" name="bump" value="1"> <span data-co-bump-text></span></label>
	<p class="jade-co__total">Total: <strong data-co-total></strong> <span class="jade-muted">USD, one-time</span></p>
	<label class="jade-field"><span>Email for your report</span><input type="email" name="email" autocomplete="email" required maxlength="190"></label>
	<label class="jade-co__agree" data-co-agree>
		<input type="checkbox" name="agree" value="1">
		<span>I agree to the <a href="/refund-policy/" target="_blank" rel="noopener">Refund Policy</a> and <a href="/terms/" target="_blank" rel="noopener">Terms</a>: <strong>refunds are {pct}% of the price, because every reading takes our astrologer's time and expertise. Redos are always free.</strong></span>
	</label>
	<p class="jade-co__need" data-co-need hidden>Please tick this box to continue.</p>
	<p class="jade-small jade-muted">Payment is processed securely by Whop. Your card statement will show <strong>{e(o['statement_descriptor'])}</strong>.</p>
	<p class="jade-error" role="alert" hidden></p>
	<div class="jf-nav"><button type="submit" class="jade-btn jade-btn--gold">Pay securely →</button></div>
</form>
</div>"""
    site.add("checkout", f"Checkout | {BRAND}", "", checkout, noindex=True)

    thanks = f"""<div class="jade jade-wrap jade-thanks" data-jade-thanks>
<h1>Thank you!</h1>
<div data-th-loading><p class="jade-muted">Confirming your order…</p></div>
<div data-th-order hidden>
	<p class="jade-intro" data-th-summary></p>
	<p>Your report will be prepared and reviewed by our astrologer, then sent to <strong data-th-email></strong> {e(o['delivery'])}. Your card statement shows <strong>{e(o['statement_descriptor'])}</strong>.</p>
</div>
<div class="jade-offer" data-jade-offers hidden></div>
<p class="jade-small jade-muted">Questions about your order? Email <a href="mailto:{EMAIL}">{EMAIL}</a>. Refunds are {pct}% of the price; redos are always free (<a href="/refund-policy/">Refund Policy</a>).</p>
</div>"""
    site.add("thank-you", f"Thank you | {BRAND}", "", thanks, noindex=True)

    uid = "jp"
    partner = f"""<div class="jade jade-wrap jade-partner">
<header class="jade-pagehead"><h1>Your partner's details</h1></header>
<p class="jade-intro">Your compatibility reading compares your chart with theirs. Enter their birth details as accurately as you can.</p>
<form data-jade-partner novalidate>
	<input type="hidden" name="order" value="">
	<label class="jade-field"><span>Their first name</span><input type="text" name="partner_name" maxlength="60" required></label>
	<label class="jade-field"><span>Their date of birth</span><input type="date" name="birth_date" required></label>
	<div class="jf-choices" role="radiogroup">
		<label class="jf-choice"><input type="radio" name="time_mode" value="exact" checked><span>I know their birth time</span></label>
		<label class="jf-choice"><input type="radio" name="time_mode" value="unknown"><span>I don't know it</span></label>
	</div>
	<label class="jade-field"><span>Their birth time</span><input type="time" name="birth_time" step="60"></label>
	{site.place_field(uid, label="Their city of birth")}
	<label class="jade-check"><input type="checkbox" name="consent" value="1"> <span>I have my partner's permission to use their birth details for this reading.</span></label>
	<p class="jade-small jade-muted">Their details are used only for your reading. We never contact them and never share their details.</p>
	<p class="jade-error" role="alert" hidden></p>
	<div class="jf-nav"><button type="submit" class="jade-btn jade-btn--gold">Send their details</button></div>
</form>
<div class="jade-ok" data-jade-partner-ok hidden><h2>Got it, thank you!</h2><p>We'll prepare your compatibility reading and email it to you.</p></div>
</div>"""
    site.add("partner", f"Partner details | {BRAND}", "", partner, noindex=True)

    refund = f"""<div class="jade jade-wrap">
<header class="jade-pagehead"><h1>Request a refund</h1></header>
<p class="jade-intro">We're sorry it didn't work for you. Tell us what we got wrong; we read every answer and it helps us get better. Refunds are {pct}% of the price. If you'd rather have a free redo instead, say so below.</p>
<form data-jade-refund novalidate>
	<label class="jade-field"><span>Email you ordered with</span><input type="email" name="email" required maxlength="190" autocomplete="email"></label>
	<label class="jade-field"><span>Order number <em class="jade-muted">(optional)</em></span><input type="text" name="order" maxlength="60"></label>
	<label class="jade-field"><span>What did we get wrong?</span><textarea name="reason" rows="5" required minlength="10" maxlength="3000"></textarea></label>
	<div class="jf-choices" role="radiogroup">
		<label class="jf-choice"><input type="radio" name="want" value="refund" checked><span>I'd like a refund</span></label>
		<label class="jf-choice"><input type="radio" name="want" value="redo"><span>I'd like a free redo instead</span></label>
	</div>
	<div class="jade-hp" aria-hidden="true"><label>Website <input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
	<p class="jade-error" role="alert" hidden></p>
	<div class="jf-nav"><button type="submit" class="jade-btn">Send my request</button></div>
</form>
<div class="jade-ok" data-jade-refund-ok hidden><h2>Request received</h2><p>We've got your request and will reply by email shortly.</p></div>
</div>"""
    site.add("refund-request", f"Request a refund | {BRAND}", "", refund, noindex=True)


# --- Everything ----------------------------------------------------------------------------------
def build_pages(site):
    # Home
    body = '<div class="jade jade-home"><section class="jade-hero jade-hero--funnel">'
    body += site.funnel("general", head="Your birth chart is rarer than you think", tag="h1", source="home")
    body += "</section>"
    body += f'<h2 class="jade-h2">Today\'s horoscope · {e(site.today_label())}</h2>' + site.sign_grid("daily")
    body += '<h2 class="jade-h2">This week</h2>' + site.sign_grid("weekly")
    body += f'<h2 class="jade-h2">This month · {e(site.now.strftime("%B %Y"))}</h2>' + site.sign_grid("monthly")
    body += '<h2 class="jade-h2">Free calculators</h2>' + site.chips([
        ("/birth-chart-calculator/", "Birth chart"), ("/rising-sign-calculator/", "Rising sign"),
        ("/moon-sign-calculator/", "Moon sign"), ("/big-three-calculator/", "Big three"),
        ("/nakshatra-calculator/", "Nakshatra"), ("/vedic-birth-chart/", "Vedic chart"),
        ("/compatibility-calculator/", "Compatibility"), ("/love-calculator/", "Love calculator"),
        ("/saturn-return-calculator/", "Saturn return"), (f"/{YEAR}-horoscope/", f"{YEAR} horoscope")], "Free calculators")
    body += (f'<section class="jade-about"><h2 class="jade-h2">About {BRAND}</h2><p>Every chart on {BRAND} is calculated from '
             "real planetary positions for your exact date, time and place of birth, using traditional Vedic and Western "
             'methods, and every reading explains its terms in plain English. <a href="/about/">How it works</a>.</p></section></div>')
    site.add("", f"{BRAND} | Daily Horoscopes & Free Personal Reading",
             "Today's horoscope for all 12 zodiac signs, plus a free personal reading calculated from your own birth chart.", body)

    # Hubs
    HUB = {
        "daily": ("horoscope-today", "today", "Horoscope Today",
                  f"Horoscope Today, {site.now.strftime('%B %-d, %Y')}: All 12 Signs | {BRAND}",
                  "Today's horoscope for all 12 zodiac signs, plus a free personal reading calculated from your own birth chart.",
                  f"Choose your sign to read today's horoscope for love, career, health and luck, updated every morning. Today is <strong>{e(site.today_label())}</strong>."),
        "weekly": ("weekly-horoscope", "this week", "Weekly Horoscope", f"Weekly Horoscope for All 12 Signs | {BRAND}",
                   "Weekly horoscopes for all 12 zodiac signs: love, career, health and luck for the week ahead.",
                   "Your week ahead for love, career, health and luck. Choose your sign to read this week's horoscope, updated every Sunday."),
        "monthly": ("monthly-horoscope", "this month", "Monthly Horoscope",
                    f"Monthly Horoscope {site.now.strftime('%B %Y')}: All 12 Signs | {BRAND}",
                    "Monthly horoscopes for all 12 zodiac signs: love, career, health and luck for the month ahead.",
                    f"Your month ahead for love, career, health and luck. Choose your sign to read the horoscope for <strong>{e(site.now.strftime('%B %Y'))}</strong>, updated on the 1st of every month."),
    }
    for period, (slug, when, h1, title, desc, intro) in HUB.items():
        site.add(slug, title, desc, f'<div class="jade"><header class="jade-pagehead"><h1>{h1}</h1></header><p class="jade-intro">{intro}</p>'
                 + site.funnel("day", when=when, source=slug) + site.sign_grid(period) + "</div>")

    # Sign pages: daily, weekly and monthly
    WHEN = {"daily": "today", "weekly": "this week", "monthly": "this month"}
    SLUG = {"daily": "{s}-horoscope-today", "weekly": "{s}-weekly-horoscope", "monthly": "{s}-monthly-horoscope"}
    LINKTXT = {"daily": "horoscope today", "weekly": "weekly horoscope", "monthly": "monthly horoscope"}
    for s in SIGNS:
        n, sd = site.sname(s), site.signs[s]
        for period in ("daily", "weekly", "monthly"):
            when = WHEN[period]
            slug = SLUG[period].format(s=s)
            h1 = {"daily": f"{n} Horoscope Today", "weekly": f"{n} Weekly Horoscope", "monthly": f"{n} Monthly Horoscope"}[period]
            out = f'<div class="jade jade-signpage"><header class="jade-pagehead"><h1>{e(h1)}</h1></header>'
            out += (f'<header class="jade-signhead"><div class="jade-signhead__glyph" aria-hidden="true">{e(sd["symbol"])}</div>'
                    f'<div><p class="jade-eyebrow">{e(sd["dates"])}</p><p class="jade-facts">{e(sd["element"])} sign · {e(sd["modality"])} · Ruled by {e(sd["ruler"])}</p></div></header>')
            out += f'<p class="jade-intro">{e(sd["profile"])}</p>'
            out += site.funnel("day", sign=s, when=when, source=slug)
            out += site.folded(site.horoscope(s, period), s, when)
            out += (f'<p class="jade-crosslink"><a href="/{s}-horoscope-tomorrow/">{e(n)} horoscope tomorrow →</a> &nbsp; '
                    f'<a href="/{s}-love-horoscope/">{e(n)} love horoscope →</a> &nbsp; <a href="/{s}-compatibility/">{e(n)} compatibility →</a></p>')
            out += '<p class="jade-crosslink">' + " &nbsp; ".join(
                f'<a href="/{SLUG[o].format(s=s)}/">{e(n)} {LINKTXT[o]} →</a>' for o in WHEN if o != period) + "</p>"
            out += '<h2 class="jade-h2">' + {"daily": "Today&#39;s horoscope for every sign", "weekly": "Weekly horoscopes for every sign",
                                             "monthly": "Monthly horoscopes for every sign"}[period] + "</h2>"
            out += site.sign_grid(period) + "</div>"
            title = {"daily": f"{n} Horoscope Today, {site.now.strftime('%B %-d, %Y')} | {BRAND}",
                     "weekly": f"{n} Weekly Horoscope | {BRAND}",
                     "monthly": f"{n} Monthly Horoscope, {site.now.strftime('%B %Y')} | {BRAND}"}[period]
            desc = {"daily": f"Today's {n} horoscope for love, career, health and luck, plus a free personal reading from your birth chart.",
                    "weekly": f"Your {n} weekly horoscope: love, career, health and luck for the week ahead.",
                    "monthly": f"Your {n} monthly horoscope for {site.now.strftime('%B %Y')}: love, career, health and luck for the month ahead."}[period]
            site.add(slug, title, desc, out)

    # Free reading
    site.add("free-reading", f"Free Personal Reading | {BRAND}",
             "A free personal reading from your own birth chart: how rare your chart is, your Sun, Moon and Rising, your birth star and your life chapters.",
             '<div class="jade jade-wrap">' + site.funnel("general", head="Your free personal reading", tag="h1", source="free-reading") +
             '<div class="jade-route-body">' + static_body(site, "C") + "</div></div>")

    # Landing pages
    for slug, (tpl, h1, desc, intent) in STATICS.items():
        f = site.funnel(intent, head=h1, tag="h1", source=slug)
        if slug == f"{YEAR}-horoscope":
            body = static_body(site, tpl) + f"<h2>{YEAR} by Sun sign</h2>" + site.sign_links(f"{YEAR}-horoscope", YEAR)
        elif slug == "love-horoscope":
            body = static_body(site, tpl) + "<h2>Today's love horoscope by sign</h2>" + site.sign_links("love-horoscope", "love")
        else:
            body = static_body(site, tpl)
        route_page(site, slug, h1, desc, body, f)

    # Per-sign landing pages
    for s in SIGNS:
        n, sd = site.sname(s), site.signs[s]
        for kind in ("moon", "rising"):
            what = "Moon" if kind == "moon" else "Rising"
            slug = f"{s}-{kind}"
            h1 = f"{n} Moon: Meaning and Personality" if kind == "moon" else f"{n} Rising: Meaning and First Impressions"
            desc = (f"What a {n} Moon means for your emotions, needs and relationships, and whether yours is really in {n}." if kind == "moon"
                    else f"What {n} rising (ascendant) means for your personality and how others see you. Check your rising sign free.")
            body = (f"<h2>What a {e(n)} {what} means</h2><p>{e(sd['inner'] if kind == 'moon' else sd['outer'])}</p><p>{e(sd['profile'])}</p>"
                    f"<h2>Is yours really {e(n)}?</h2><p>" + (
                        "The Moon changes sign every two to three days, and Western and Vedic astrology place it about 24° apart, so many people have a different Moon sign in each system. Your calculation above shows both."
                        if kind == "moon" else
                        "Your rising sign changes about every two hours, so it depends on your exact birth time and place, and Western and Vedic astrology often give different answers. Your calculation above shows both.")
                    + "</p>" + site.sign_links(kind, what))
            route_page(site, slug, h1, desc, body, site.funnel(kind, head=h1, tag="h1", sign=s, source=slug))
        slug = f"{s}-{YEAR}-horoscope"
        h1 = f"{n} {YEAR} Horoscope"
        body = f"<h2>{e(n)} in {YEAR}</h2>" + "".join(f"<p>{e(p)}</p>" for p in year_text(site, s)) + site.sign_links(f"{YEAR}-horoscope", YEAR)
        route_page(site, slug, h1, f"The {n} {YEAR} horoscope: what Saturn and Jupiter bring {n} in {YEAR}, and your own chart's {YEAR} timeline.",
                   body, site.funnel("year", head=h1, tag="h1", sign=s, source=slug))
        # Tomorrow and love: page head + funnel (h2) + folded generic horoscope
        tom = (site.now + __import__("datetime").timedelta(days=1)).strftime("%B %-d, %Y")
        head = f'<header class="jade-pagehead"><p class="jade-eyebrow">{e(sd["dates"])}</p><h1>{e(n)} Horoscope Tomorrow</h1></header>'
        body = site.folded(site.horoscope(s, "tomorrow"), s, "tomorrow") + \
            f'<p class="jade-crosslink"><a href="/{s}-horoscope-today/">{e(n)} horoscope today →</a></p>' + site.sign_links("horoscope-tomorrow", "tomorrow")
        route_page(site, f"{s}-horoscope-tomorrow", f"{n} Horoscope Tomorrow",
                   f"Tomorrow's {n} horoscope for love, career, health and luck, plus a free reading from your own chart.",
                   body, site.funnel("day", sign=s, when="tomorrow", source=f"{s}-horoscope-tomorrow"),
                   title=f"{n} Horoscope Tomorrow, {tom} | {BRAND}", pagehead=head)
        head = f'<header class="jade-pagehead"><p class="jade-eyebrow">{e(sd["dates"])}</p><h1>{e(n)} Love Horoscope Today</h1></header>'
        body = site.folded(site.horoscope(s, "daily", only=("personal", "emotions")), s, "today") + \
            f'<p class="jade-crosslink"><a href="/{s}-compatibility/">{e(n)} compatibility →</a> &nbsp; <a href="/{s}-soulmate/">{e(n)} soulmate →</a></p>' + \
            site.sign_links("love-horoscope", "love")
        route_page(site, f"{s}-love-horoscope", f"{n} Love Horoscope Today",
                   f"Today's {n} love horoscope, plus what your own birth chart says about love and marriage.",
                   body, site.funnel("love", sign=s, when="today", source=f"{s}-love-horoscope"),
                   title=f"{n} Love Horoscope Today, {site.now.strftime('%B %-d')} | {BRAND}", pagehead=head)

    # Nakshatras
    for nslug, nk in site.naks.items():
        planet = site.ref["planets"].get(nk["lord"], {}).get("name", nk["lord"].title())
        h1 = f"{nk['name']} Nakshatra: Meaning, Traits and Ruling Planet"
        body = (f"<h2>About {e(nk['name'])}</h2><p>{e(nk['traits'])}</p>"
                f'<dl class="jade-facts-list"><div><dt>Ruling planet</dt><dd>{e(planet)}</dd></div>'
                f"<div><dt>Deity</dt><dd>{e(nk['deity'][:1].upper() + nk['deity'][1:])}</dd></div>"
                f"<div><dt>Symbol</dt><dd>{e(nk['symbol'][:1].upper() + nk['symbol'][1:])}</dd></div></dl>"
                "<p>Your Nakshatra is set by where the Moon was at the minute you were born. It moves through one Nakshatra in about a day, "
                "so two people born on the same day can have different birth stars. Calculate yours above to check.</p>" + site.nak_links())
        route_page(site, f"nakshatra/{nslug}", h1,
                   f"{nk['name']} Nakshatra meaning: personality traits, ruling planet, deity and symbol. Find out if it is your birth star.",
                   body, site.funnel("nakshatra", head=h1, tag="h1", source=f"nakshatra-{nslug}"))

    build_compat(site)
    legal(site)
    order_pages(site)
