/* Test mode only (brain_url "test"): answers every request with sample data so all pages
   can be clicked through before the AWS brain exists. Never loaded once the brain is connected. */
(function () {
	'use strict';
	function esc(s) { return String(s || '').replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
	function ok(data) { return { success: true, data: data }; }
	var CITIES = ['New York, NY, USA', 'Los Angeles, CA, USA', 'Chicago, IL, USA', 'Houston, TX, USA', 'Phoenix, AZ, USA', 'Dehradun, Uttarakhand, India', 'London, UK'];
	var TOPIC = { love: 'love', career: 'career', money: 'money', health: 'energy', year: 'next 12 months' };

	window.JadeMock = function (action, p) {
		switch (action) {
			case 'place_suggest':
				return ok({ items: CITIES.filter(function (c) { return c.toLowerCase().indexOf(String(p.q).toLowerCase()) >= 0; })
					.map(function (c, i) { var parts = c.split(', '); return { id: 'mock' + i, main: parts[0], sub: parts.slice(1).join(', '), full: c }; }) });
			case 'config':
				return ok({ maps_key: '' });
			case 'prepare':
				return ok({ token: 'mock-token', ai: false });
			case 'reading': {
				var topics = (p.topics || []).map(function (t) { return TOPIC[t] || t; }).join(', ') || 'general';
				return ok({ token: 'mock-token', rarity: 52000, html:
					'<article class="jr" data-jade-reading data-token="mock-token" data-rarity="1 in 52,000">' +
					'<section class="jr-hero"><p class="jr-eyebrow">Sample reading (test mode)</p><h2 class="jr-headline">' + esc(p.first_name) + ', your chart: about <span class="jr-num">1 in 52,000</span></h2>' +
					'<p class="jr-lead">This is placeholder text. The real reading comes from the brain. You chose: ' + esc(topics) + '. Gender: ' + esc(p.gender) + '.' +
					(p.lat ? ' Exact spot: ' + esc(p.lat) + ', ' + esc(p.lng) + '.' : '') + '</p></section>' +
					'<section class="jr-sec jr-cliff"><h3>What your chart says next (locked)</h3><p>Sample cliffhanger on your chosen topics.</p>' +
					'<form class="jr-form" data-jade-capture novalidate><label class="jade-field"><span>Email</span><input type="email" name="email" required></label>' +
					'<label class="jade-check"><input type="checkbox" name="consent" value="1"> <span>Email me my reading and personal insights. Unsubscribe anytime.</span></label>' +
					'<p class="jade-error" hidden></p><button class="jade-btn" type="submit">Unlock the rest</button></form></section>' +
					'<section class="jr-cta"><h3>Your full Vedic Life Report</h3><p>Prepared and reviewed by our astrologer.</p>' +
					'<a class="jade-btn jade-btn--gold" data-jade-buy="main" href="/checkout/?t=mock-token&o=main">Get my full report · $49</a></section></article>' });
			}
			case 'capture':
				return ok({ html: '<article class="jr" data-jade-reading data-token="mock-token"><section class="jr-sec jr-next"><h3>Unlocked (sample)</h3><p>The rest of the free reading appears here.</p></section>' +
					'<section class="jr-cta"><a class="jade-btn jade-btn--gold" data-jade-buy="main" href="/checkout/?t=mock-token&o=main">Get my full report · $49</a></section></article>' });
			case 'ai':
				return ok({ parts: {} });
			case 'compatibility':
				return ok({ token: 'mock-compat', score: 27, html:
					'<article class="jr" data-jade-reading data-token="mock-compat"><section class="jr-hero"><p class="jr-eyebrow">Sample match (test mode)</p>' +
					'<h2 class="jr-headline">' + esc(p.a_name) + ' &amp; ' + esc(p.b_name) + ': <span class="jr-num">27 / 36</span></h2>' +
					'<p class="jr-lead">Placeholder text. The real match is calculated by the brain from both charts.</p></section>' +
					'<section class="jr-cta"><h3>Your full compatibility reading</h3><a class="jade-btn jade-btn--gold" data-jade-buy="compat" href="/checkout/?t=mock-compat&o=compat">Get our full reading · $29</a></section></article>' });
			case 'offer':
				if (p.offer === 'compat') return ok({ lines: [{ name: 'What Your Partner Can’t Put Into Words (compatibility reading + 1 personal question)', price: 29 }], bump: null, email: '', variant: 'compat-a' });
				return ok({ lines: [{ name: 'Your Vedic Life Report', price: 49 }], bump: { name: 'The Next 12 Months: When to Push, When to Wait', price: 19, blurb: 'month by month, from today' }, email: '', variant: 'main-a' });
			case 'checkout':
				window.__jadeLastCheckout = p;
				return ok({ url: '/thank-you/?order=TEST1001' });
			case 'order':
				return ok({ order: p.order || 'TEST1001', value: 49, email: 'you@example.com', session: 'mock-session',
					summary: 'Order ' + (p.order || 'TEST1001') + ': Your Vedic Life Report ($49).',
					offers: [
						{ key: 'compat', title: 'What Your Partner Can’t Put Into Words', blurb: 'Their chart says what they feel, need and fear in love, and how your two charts fit together.', points: ['Chemistry and clashes', 'Your strongest years together', 'Plus 1 personal question, answered from both charts'], price: 29, button: 'Yes, add it for $29', decline: 'No thanks' },
						{ key: 'downsell', title: 'Are You Two Written in the Stars?', blurb: 'The same compatibility reading, without the personal question.', price: 19, button: 'Yes, add it for $19', decline: 'No thanks, I’m done' }
					] });
			case 'upsell':
				return ok({ order: 'TEST1002', value: p.offer === 'compat' ? 29 : 19, title: p.offer === 'compat' ? 'Compatibility reading' : 'Compatibility reading (essentials)', partner: '/partner/?order=TEST1002' });
			case 'partner':
			case 'refund_request':
				return ok({});
		}
		return { success: false, data: { message: 'Test mode: no sample for ' + action } };
	};
})();
