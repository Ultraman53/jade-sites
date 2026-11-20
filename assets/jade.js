/* Jade Astrology front end.
   Free-reading funnel, compatibility calculator, checkout, thank-you offers, partner and refund forms.
   Every request goes to the AWS brain (window.JadeCfg.brain). With JadeCfg.test, jade-mock.js answers instead. */
(function () {
	'use strict';
	var CFG = window.JadeCfg || {};

	/* ---------- Mobile menu ---------- */
	function navToggle() {
		var b = document.querySelector('.nav-toggle'), n = document.getElementById('site-nav');
		if (!b || !n) return;
		b.addEventListener('click', function () {
			var open = n.classList.toggle('is-open');
			b.setAttribute('aria-expanded', open ? 'true' : 'false');
		});
	}

	/* ---------- Talking to the brain ---------- */
	var FAIL = { success: false, data: { message: 'Our server had a problem. Please try again in a minute.' } };
	function api(action, payload) {
		payload = payload || {};
		payload.site = CFG.site;
		payload.page = location.pathname;
		if (CFG.test) {
			return new Promise(function (res) { setTimeout(function () { res(window.JadeMock ? window.JadeMock(action, payload) : FAIL); }, 400); });
		}
		return fetch(CFG.brain + '/v1/' + action.replace(/_/g, '-'), {
			method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), credentials: 'omit'
		}).then(function (r) {
			return r.text().then(function (t) { try { return JSON.parse(t); } catch (e) { return FAIL; } });
		});
	}

	/* Form fields as an object; checkbox groups become lists. */
	function fields(form, out) {
		out = out || {};
		form.querySelectorAll('input, select, textarea').forEach(function (el) {
			if (!el.name || el.disabled) return;
			if (el.type === 'checkbox') {
				var group = form.querySelectorAll('input[type="checkbox"][name="' + el.name + '"]').length > 1;
				if (group) { out[el.name] = out[el.name] || []; if (el.checked) out[el.name].push(el.value); }
				else out[el.name] = el.checked ? el.value : '';
			} else if (el.type === 'radio') {
				if (el.checked) out[el.name] = el.value;
			} else out[el.name] = el.value;
		});
		return out;
	}

	var UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'kw', 'mt', 'ag', 'dev'];
	function attribution() {
		var params = new URLSearchParams(location.search), stored = {}, changed = false;
		try { stored = JSON.parse(sessionStorage.getItem('jade_attr') || '{}'); } catch (e) {}
		UTM_KEYS.forEach(function (k) { if (params.get(k)) { stored[k] = params.get(k).slice(0, 250); changed = true; } });
		if (changed) { try { sessionStorage.setItem('jade_attr', JSON.stringify(stored)); } catch (e) {} }
		var copy = {}; Object.keys(stored).forEach(function (k) { copy[k] = stored[k]; });
		return copy;
	}
	function track(event, params) {
		window.dataLayer = window.dataLayer || [];
		var o = { event: event };
		Object.keys(params || {}).forEach(function (k) { o[k] = params[k]; });
		window.dataLayer.push(o);
		if (typeof window.gtag === 'function') window.gtag('event', event, params || {});
	}
	function setBusy(form, busy, label) {
		var btn = form.querySelector('button[type="submit"]');
		if (!btn) return;
		if (!btn.dataset.label) btn.dataset.label = btn.textContent;
		btn.disabled = busy;
		btn.textContent = busy ? label : btn.dataset.label;
	}
	function showError(scope, msg) {
		var el = scope.querySelector('.jade-error');
		if (!el) return;
		el.textContent = msg || '';
		el.hidden = !msg;
	}
	function newSession() {
		var a = new Uint8Array(16);
		window.crypto.getRandomValues(a);
		return Array.prototype.map.call(a, function (b) { return ('0' + b.toString(16)).slice(-2); }).join('');
	}
	function deviceInfo() {
		var tz = ''; try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (e) {}
		return ['screen ' + screen.width + 'x' + screen.height + '@' + (window.devicePixelRatio || 1),
			'tz ' + tz, 'lang ' + (navigator.language || ''), 'platform ' + (navigator.platform || ''),
			'touch ' + (('ontouchstart' in window) ? 'yes' : 'no')].join('; ').slice(0, 250);
	}
	function q(form, n) { return form.querySelector('[name="' + n + '"]'); }

	/* ---------- Birthplace suggestions ---------- */
	function placeAutocomplete(scope, prefix) {
		prefix = prefix || '';
		var input = q(scope, prefix + 'birth_place');
		if (!input) return;
		var list = input.parentNode.querySelector('.jade-place__list');
		var idField = q(scope, prefix + 'place_id'), sessField = q(scope, prefix + 'place_session');
		var timer = null, seq = 0, items = [], active = -1, chosen = '';
		sessField.value = newSession();
		function close() { list.hidden = true; list.innerHTML = ''; input.setAttribute('aria-expanded', 'false'); input.removeAttribute('aria-activedescendant'); active = -1; }
		function highlight(i) {
			var opts = list.querySelectorAll('[role="option"]');
			opts.forEach(function (o, n) { o.setAttribute('aria-selected', n === i ? 'true' : 'false'); });
			active = i;
			if (opts[i]) input.setAttribute('aria-activedescendant', opts[i].id);
		}
		function choose(i) {
			var it = items[i]; if (!it) return;
			chosen = it.full || (it.main + (it.sub ? ', ' + it.sub : ''));
			input.value = chosen; idField.value = it.id || '';
			close();
		}
		function render() {
			list.innerHTML = '';
			if (!items.length) return close();
			items.forEach(function (it, i) {
				var li = document.createElement('li');
				li.id = list.id + '-' + i; li.setAttribute('role', 'option'); li.setAttribute('aria-selected', 'false');
				var main = document.createElement('span'); main.className = 'jade-place__main'; main.textContent = it.main; li.appendChild(main);
				if (it.sub) { var sub = document.createElement('span'); sub.className = 'jade-place__sub'; sub.textContent = it.sub; li.appendChild(sub); }
				li.addEventListener('mousedown', function (e) { e.preventDefault(); choose(i); });
				list.appendChild(li);
			});
			list.hidden = false; input.setAttribute('aria-expanded', 'true');
		}
		input.addEventListener('input', function () {
			if (input.value !== chosen) idField.value = '';
			clearTimeout(timer);
			var text = input.value.trim();
			if (text.length < 2) { seq++; return close(); }
			timer = setTimeout(function () {
				var mine = ++seq;
				api('place_suggest', { q: text, session: sessField.value }).then(function (res) {
					if (mine !== seq) return;
					items = (res && res.success && res.data.items) || [];
					render();
				}).catch(close);
			}, 250);
		});
		input.addEventListener('keydown', function (e) {
			if (list.hidden) return;
			if (e.key === 'ArrowDown') { e.preventDefault(); highlight(Math.min(active + 1, items.length - 1)); }
			else if (e.key === 'ArrowUp') { e.preventDefault(); highlight(Math.max(active - 1, 0)); }
			else if (e.key === 'Enter') { if (active >= 0) { e.preventDefault(); choose(active); } }
			else if (e.key === 'Escape') close();
		});
		input.addEventListener('blur', function () { setTimeout(close, 120); });
	}

	/* ---------- Advanced search: pin the exact place of birth on a satellite map ---------- */
	/* Google Maps is loaded only when this panel is opened. The address search is Google's current PlaceAutocompleteElement (Places API (New)); the old places.Autocomplete is no longer used.
	   If that element cannot start, the plain text box stays and searches by pressing Enter. */
	var mapsLoading = null;
	function loadMaps() {
		if (mapsLoading) return mapsLoading;
		mapsLoading = api('config', {}).then(function (res) {
			var key = res && res.success && res.data.maps_key;
			if (!key) throw new Error('nokey');
			return new Promise(function (ok, bad) {
				if (window.google && window.google.maps && window.google.maps.importLibrary) return ok();
				window.__jadeMapsReady = ok;
				var s = document.createElement('script');
				s.src = 'https://maps.googleapis.com/maps/api/js?key=' + encodeURIComponent(key) + '&loading=async&callback=__jadeMapsReady';
				s.async = true; s.onerror = bad;
				document.head.appendChild(s);
				setTimeout(function () { bad(new Error('timeout')); }, 12000);
			});
		}).then(function () {
			var gm = window.google.maps;
			return Promise.all([gm.importLibrary('maps'), gm.importLibrary('places'), gm.importLibrary('geocoding'), gm.importLibrary('marker')]).then(function (l) {
				return { Map: l[0].Map, PlaceAutocompleteElement: l[1].PlaceAutocompleteElement, Geocoder: l[2].Geocoder, Marker: l[3].Marker || gm.Marker };
			});
		});
		mapsLoading.catch(function () { mapsLoading = null; });
		return mapsLoading;
	}
	/* A place is given when the city box has a name OR the exact spot is pinned (lat and lng set). A pin whose city text was changed afterwards is dropped first (see exactPlace). */
	function hasPlace(form, prefix) {
		prefix = prefix || '';
		form.querySelectorAll('[data-jade-exact]').forEach(function (b) { if ((b.getAttribute('data-prefix') || '') === prefix && b.__jadeSyncPin) b.__jadeSyncPin(); });
		var c = q(form, prefix + 'birth_place'), la = q(form, prefix + 'lat'), ln = q(form, prefix + 'lng');
		if (c && c.value.trim().length >= 2) return true;
		return !!(la && ln && la.value && ln.value && isFinite(parseFloat(la.value)) && isFinite(parseFloat(ln.value)));
	}
	/* the name of a reverse-geocoded spot: city (or district), state or region, country; '' if Google gave nothing usable */
	function placeLabel(results) {
		function part(types) {
			for (var i = 0; i < (results || []).length; i++) {
				var comps = results[i].address_components || [];
				for (var j = 0; j < comps.length; j++) {
					for (var k = 0; k < types.length; k++) if ((comps[j].types || []).indexOf(types[k]) > -1 && comps[j].long_name) return comps[j].long_name;
				}
			}
			return '';
		}
		var town = part(['locality', 'postal_town', 'sublocality', 'administrative_area_level_3', 'administrative_area_level_2']);
		var region = part(['administrative_area_level_1']), country = part(['country']);
		if (!town && !region) return '';
		var out = [];
		[town, region, country].forEach(function (x) { if (x && out.indexOf(x) < 0) out.push(x); });
		return out.join(', ');
	}
	function exactPlace(box, form) {
		var prefix = box.getAttribute('data-prefix') || '';
		var panel = box.querySelector('.jade-exact__panel');
		var status = box.querySelector('[data-exact-status]');
		var map = null, marker = null, picked = null, geocoder = null;
		var pinned = false, pinnedLabel = '', autoFilled = false;
		var openBtn = box.querySelector('[data-exact-open]'), openText = openBtn.textContent;
		var city = q(form, prefix + 'birth_place');
		function asLatLng(v) { return v && typeof v.lat === 'function' ? v : new window.google.maps.LatLng(v.lat, v.lng); }
		function setPick(latLng) {
			picked = latLng;
			marker.setPosition(latLng);
			status.textContent = 'Pinned at ' + latLng.lat().toFixed(5) + ', ' + latLng.lng().toFixed(5) + '. Drag the pin to adjust.';
		}
		/* if the visitor changes the city text after pinning, the pin no longer describes that city: drop it */
		function syncPin() {
			if (!pinned || !city) return;
			if ((city.value || '').trim() === pinnedLabel) return;
			q(form, prefix + 'lat').value = ''; q(form, prefix + 'lng').value = '';
			pinned = false; autoFilled = false;
			openBtn.textContent = openText;
		}
		box.__jadeSyncPin = syncPin;
		if (city) ['input', 'change', 'blur'].forEach(function (ev) { city.addEventListener(ev, syncPin); });
		function searchBox(L) {
			var input = box.querySelector('.jade-exact__search');
			var pac = null;
			try { pac = new L.PlaceAutocompleteElement({}); } catch (e) { pac = null; }
			if (pac) {
				/* the element draws its own text box (it cannot be attached to ours), so it takes the place of the old one */
				pac.placeholder = input.getAttribute('placeholder') || '';
				pac.setAttribute('aria-label', input.getAttribute('aria-label') || 'Search');
				pac.style.width = '100%';
				pac.style.colorScheme = 'light';
				input.parentNode.insertBefore(pac, input);
				input.style.display = 'none';
				pac.addEventListener('gmp-select', function (ev) {
					var place = ev && ev.placePrediction && ev.placePrediction.toPlace();
					if (!place) return;
					place.fetchFields({ fields: ['location'] }).then(function () {
						if (!place.location) throw new Error('noloc');
						var ll = asLatLng(place.location);
						map.setCenter(ll); map.setZoom(18);
						setPick(ll);
					}).catch(function () { status.textContent = 'We couldn’t open that place. Tap the map to pin it instead.'; });
				});
				return;
			}
			function go() {
				var text = (input.value || '').trim();
				if (!text) return;
				new L.Geocoder().geocode({ address: text }, function (r, st) {
					if (st === 'OK' && r[0]) { map.setCenter(r[0].geometry.location); map.setZoom(17); status.textContent = 'Found it. Tap the map or drag the pin onto the exact spot.'; }
					else status.textContent = 'We couldn’t find that. Try the city name, or tap the map.';
				});
			}
			input.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); go(); } });
			input.addEventListener('change', go);
		}
		openBtn.addEventListener('click', function () {
			panel.hidden = false;
			track('jade_exact_open');
			loadMaps().then(function (L) {
				if (map) return;
				map = new L.Map(box.querySelector('.jade-exact__map'), { center: { lat: 39.5, lng: -98.35 }, zoom: 4, mapTypeId: 'hybrid', streetViewControl: false, fullscreenControl: false });
				marker = new L.Marker({ map: map, draggable: true });
				map.addListener('click', function (ev) { setPick(ev.latLng); });
				marker.addListener('dragend', function (ev) { setPick(ev.latLng); });
				geocoder = new L.Geocoder();
				searchBox(L);
				if (city && city.value) {
					new L.Geocoder().geocode({ address: city.value }, function (r, st) {
						if (st === 'OK' && r[0]) { map.setCenter(r[0].geometry.location); map.setZoom(13); }
					});
				}
			}).catch(function () {
				status.textContent = 'The map isn’t available right now. Your city is enough to continue.';
			});
		});
		box.querySelector('[data-exact-cancel]').addEventListener('click', function () { panel.hidden = true; });
		box.querySelector('[data-exact-use]').addEventListener('click', function () {
			if (!picked) { status.textContent = 'Tap the map to drop the pin on the exact place first.'; return; }
			var la = picked.lat(), ln = picked.lng();
			q(form, prefix + 'lat').value = la.toFixed(6);
			q(form, prefix + 'lng').value = ln.toFixed(6);
			pinned = true;
			/* the reading needs a place name as well: keep a city the visitor typed; otherwise name the spot now (so "Next" works at once), then improve the name from a reverse geocode */
			var fallback = 'Pinned location (' + la.toFixed(4) + ', ' + ln.toFixed(4) + ')';
			if (city) {
				var cur = (city.value || '').trim();
				if (!cur || (autoFilled && cur === pinnedLabel)) { city.value = fallback; autoFilled = true; } else autoFilled = false;
				pinnedLabel = (city.value || '').trim();
				if (autoFilled && geocoder) {
					var mine = pinnedLabel;
					try {
						geocoder.geocode({ location: { lat: la, lng: ln } }, function (r, st) {
							var name = st === 'OK' ? placeLabel(r) : '';
							if (name && pinned && autoFilled && (city.value || '').trim() === mine) { city.value = name; pinnedLabel = name; }
						});
					} catch (e) { /* the fallback label stays */ }
				}
			}
			panel.hidden = true;
			openBtn.textContent = 'Exact place pinned ✓ (change)';
			track('jade_exact_pinned');
		});
	}

	/* ---------- Keyword-matched headlines (from the ad's kw= value) ---------- */
	var SIGNS = ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces'];
	var KW = [
		{ r: /saturn return/, h: 'When is your Saturn return? Find your dates', s: 'Calculated from where Saturn was at your birth. Free, about 30 seconds, no email needed.', f: 'saturn' },
		{ r: /2027|next year/, h: 'Your 2027, from your own birth chart', s: 'Not one forecast for everyone with your sign: the exact planetary periods your chart runs through in 2027.', f: '2027' },
		{ r: /marr|spouse|husband|wife|wedding/, h: 'When will you marry? Ask your 7th house', s: 'Your chart’s marriage house, its ruler and your next turning point. Free, no email needed.', t: 'love' },
		{ r: /soul ?mate|twin flame|love|relationship|crush|romance|dating/, h: '{Sign}Your love story is written in your 7th house', s: 'See what your own chart says about love, and how rare your chart is. Free, no email needed.', t: 'love' },
		{ r: /career|job|work|profession|business/, h: 'What your birth chart says about your career', s: 'Your 10th house, its ruler and the chapter you’re in now. Free, about 30 seconds.', t: 'career' },
		{ r: /money|wealth|rich|financ|lottery|lucky number/, h: 'What your birth chart says about money', s: 'Your wealth houses, their rulers and your timing. Free, about 30 seconds.', t: 'money' },
		{ r: /nakshatra|birth star|lunar mansion/, h: 'Find your Nakshatra (birth star)', s: 'Your birth star, its ruling planet and what it says about you. Free, no email needed.' },
		{ r: /kundli|kundali|janam|janma|jyotish|vedic|sidereal|lagna|rashi/, h: 'Your free Vedic birth chart, read for you', s: 'Lagna, Rashi, Nakshatra, yogas and your dasha timeline, explained in plain English.' },
		{ r: /rising|ascendant/, h: 'Find your rising sign in 30 seconds', s: 'Western and Vedic, from your exact birth time and place. Plus how rare your chart is.' },
		{ r: /moon sign|moon calculator|my moon|lunar sign/, h: 'Find your Moon sign in 30 seconds', s: 'Western and Vedic, plus your birth star. Free, no email needed.' },
		{ r: /big (3|three)|sun moon (and )?rising|sun moon rising/, h: 'Your Sun, Moon and Rising, calculated free', s: 'From your exact birth chart, in both Western and Vedic astrology.' },
		{ r: /birth ?chart|natal|chart reading|astrology chart|zodiac chart/, h: 'Your free birth chart, read for you', s: 'Every placement explained, and how rare your chart really is. No email needed.' },
		{ r: /tomorrow/, h: '{Sign}Tomorrow’s horoscope is for 1 in 12 people. Your chart is rarer.', s: 'See how rare your own chart is and what it says comes next. Free, no email needed.' },
		{ r: /horoscope|zodiac|astrology|today|daily|weekly|star sign/, h: '{Sign}Your horoscope is shared by 1 in 12 people. Your chart isn’t.', s: 'See how rare your own birth chart is, and what it says about you. Free, about 30 seconds.' }
	];
	function lcFirst(t) { return t.charAt(0).toLowerCase() + t.slice(1); }
	function keywordMatch() {
		var kw = (attribution().kw || '').toLowerCase().replace(/[+\[\]"]/g, ' ').replace(/\s+/g, ' ').trim();
		if (!kw) return null;
		var sign = '';
		SIGNS.forEach(function (s) { if (!sign && new RegExp('\\b' + s + '\\b').test(kw)) sign = s.charAt(0).toUpperCase() + s.slice(1); });
		for (var i = 0; i < KW.length; i++) {
			if (KW[i].r.test(kw)) {
				var m = KW[i];
				var h = m.h.indexOf('{Sign}') === 0 ? (sign ? sign + ', ' + lcFirst(m.h.slice(6)) : m.h.slice(6)) : m.h;
				return { h: h, s: m.s, t: m.t || '', f: m.f || '' };
			}
		}
		return null;
	}
	function applyKeyword() {
		var m = keywordMatch(); if (!m) return;
		var funnels = document.querySelectorAll('[data-jade-funnel]'), first = funnels[0];
		if (first) {
			var head = first.querySelector('[data-jade-kw-head]'), sub = first.querySelector('[data-jade-kw-sub]');
			if (head && (head.tagName === 'H1' || !document.querySelector('.jade-pagehead h1'))) { head.textContent = m.h; if (sub) sub.textContent = m.s; first.dataset.hv = 'kw'; }
		}
		funnels.forEach(function (f) {
			if (m.t && (!f.dataset.topic || f.dataset.topic === 'general')) f.dataset.topic = m.t;
			if (m.f && !f.dataset.focus) f.dataset.focus = m.f;
		});
	}

	/* ---------- Free-reading funnel ---------- */
	var STEPS = ['date', 'place', 'time', 'focus', 'you'];
	var MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
	var SUN = [[1, 20, 'Capricorn'], [2, 19, 'Aquarius'], [3, 21, 'Pisces'], [4, 20, 'Aries'], [5, 21, 'Taurus'], [6, 21, 'Gemini'], [7, 23, 'Cancer'], [8, 23, 'Leo'], [9, 23, 'Virgo'], [10, 23, 'Libra'], [11, 22, 'Scorpio'], [12, 22, 'Sagittarius'], [12, 32, 'Capricorn']];
	function sunSign(m, d) { for (var i = 0; i < SUN.length; i++) { if (m < SUN[i][0] || (m === SUN[i][0] && d < SUN[i][1])) return SUN[i][2]; } return 'Capricorn'; }
	function dateValueOf(form, p) {
		p = p || '';
		var y = +q(form, p + 'b_year').value, m = +q(form, p + 'b_month').value, d = +q(form, p + 'b_day').value;
		if (!y || !m || !d) return '';
		var dt = new Date(Date.UTC(y, m - 1, d));
		if (dt.getUTCMonth() !== m - 1 || dt > new Date()) return 'bad';
		return y + '-' + ('0' + m).slice(-2) + '-' + ('0' + d).slice(-2);
	}

	function funnel(root) {
		var form = root.querySelector('.jf-form');
		var err = form.querySelector('.jade-error');
		var calc = root.querySelector('.jf-calc');
		var result = root.querySelector('.jf-result');
		var bar = root.querySelector('.jf-progress span');
		var headEl = root.querySelector('[data-jade-kw-head]'), subEl = root.querySelector('[data-jade-kw-sub]');
		var cur = 0, started = false;
		placeAutocomplete(form);
		form.querySelectorAll('[data-jade-exact]').forEach(function (b) { exactPlace(b, form); });

		if (root.dataset.variants && root.dataset.hv !== 'kw' && headEl) {
			var vars = {}; try { vars = JSON.parse(root.dataset.variants); } catch (e) {}
			var keys = Object.keys(vars), v = '';
			try { v = sessionStorage.getItem('jade_hv') || ''; } catch (e) {}
			if (keys.indexOf(v) < 0) { v = keys[Math.floor(Math.random() * keys.length)]; try { sessionStorage.setItem('jade_hv', v); } catch (e) {} }
			if (vars[v]) { headEl.textContent = vars[v]; root.dataset.hv = v; }
		}

		function dateText() { return MONTHS[+q(form, 'b_month').value - 1] + ' ' + (+q(form, 'b_day').value) + ', ' + q(form, 'b_year').value; }
		function city() { return (q(form, 'birth_place').value.split(',')[0] || '').trim(); }
		function timeMode() { var r = form.querySelector('[name="time_mode"]:checked'); return r ? r.value : 'exact'; }
		function timeText() {
			var mode = timeMode(); if (mode === 'unknown') return '';
			var t = mode === 'exact' ? q(form, 'birth_time').value : q(form, 'rough_time').value;
			var h = +t.split(':')[0], mi = t.split(':')[1];
			var s = (h % 12 || 12) + ':' + mi + ' ' + (h < 12 ? 'AM' : 'PM');
			return mode === 'exact' ? s : 'around ' + s;
		}
		function setHead(h, s) { if (!headEl) return; headEl.textContent = h; if (subEl && s !== undefined) subEl.textContent = s; root.classList.add('is-personal'); }
		function personalize(step) {
			var births = Number(CFG.births || 360000).toLocaleString('en-US');
			if (step === 'date') {
				var m = +q(form, 'b_month').value, d = +q(form, 'b_day').value, sun = sunSign(m, d), page = root.dataset.sign || '';
				var note = 'Next: where you were born. It changes your chart more than most people think.';
				if (page && sun.toLowerCase() !== page) note = 'Heads up: by your birth date your Sun is in ' + sun + ', not ' + page.charAt(0).toUpperCase() + page.slice(1) + '. Your Vedic Sun may be different again. You’ll see both.';
				setHead(dateText() + '. You’re one of about ' + births + ' people born that day.', note);
			} else if (step === 'place' && city()) {
				setHead(dateText() + ', near ' + city() + '. Only a handful of people share that.', 'Now the time. Your rising sign changes about every two hours.');
			} else if (step === 'time') {
				var t = timeText();
				setHead(t ? (t.indexOf('around') === 0 ? 'Born ' + t + ' near ' + (city() || 'your birthplace') + '. Let’s see what your chart says.' : 'At ' + t + ', maybe only you. Let’s see what your chart says.')
					: 'Even without the minute, your Moon and birth star narrow it down. Let’s see what your chart says.', 'What matters most to you right now? Your reading starts there.');
			} else if (step === 'focus') {
				setHead('Almost there.', 'Last step: your name, so your reading can use it.');
			}
		}
		function say(msg) { err.textContent = msg || ''; err.hidden = !msg; }
		function show(i) {
			cur = i;
			STEPS.forEach(function (s, n) { form.querySelector('[data-step="' + s + '"]').hidden = n !== i; });
			if (bar) bar.style.width = ((i + 1) / (STEPS.length + 1) * 100) + '%';
			say('');
			var step = form.querySelector('[data-step="' + STEPS[i] + '"]');
			var first = step.querySelector('select:not([hidden]), input[type="text"], input[type="time"]');
			if (first && i > 0) setTimeout(function () { try { first.focus({ preventScroll: true }); } catch (e) {} }, 50);
		}
		function syncTime() { var mode = timeMode(); form.querySelectorAll('[data-when]').forEach(function (el) { el.hidden = el.dataset.when !== mode; }); }
		form.querySelectorAll('[name="time_mode"]').forEach(function (r) { r.addEventListener('change', syncTime); });
		syncTime();

		function validate(i) {
			var s = STEPS[i];
			if (s === 'date') { var v = dateValueOf(form); if (!v) return 'Please choose your month, day and year of birth.'; if (v === 'bad') return 'That date doesn’t exist. Please check the day.'; }
			if (s === 'place' && !hasPlace(form)) return 'Please enter the city you were born in.';
			if (s === 'time' && timeMode() === 'exact' && !q(form, 'birth_time').value) return 'Please enter your birth time, or choose “I know roughly” or “I don’t know”.';
			if (s === 'focus' && !form.querySelector('[name="topics"]:checked')) return 'Pick at least one, so your reading starts with what matters to you.';
			if (s === 'you' && q(form, 'first_name').value.trim().length < 1) return 'Please enter your first name, so your reading can be written for you.';
			return '';
		}
		function birthFields() {
			var mode = timeMode();
			return {
				birth_date: dateValueOf(form), time_mode: mode,
				birth_time: mode === 'exact' ? q(form, 'birth_time').value : (mode === 'rough' ? q(form, 'rough_time').value : ''),
				birth_place: q(form, 'birth_place').value.trim(), place_id: q(form, 'place_id').value,
				place_session: q(form, 'place_session').value, lat: q(form, 'lat').value, lng: q(form, 'lng').value
			};
		}
		var prep = null;
		function prepare() {
			var b = birthFields(), key = JSON.stringify(b);
			if (prep && prep.key === key) return prep.promise;
			var data = attribution();
			Object.keys(b).forEach(function (k) { data[k] = b[k]; });
			data.hv = root.dataset.hv || ''; data.intent = root.dataset.intent || 'general'; data.when = root.dataset.when || 'today';
			data.topic = root.dataset.topic || 'general'; data.focus = root.dataset.focus || ''; data.source_page = root.dataset.source || '';
			var p = api('prepare', data).catch(function () { return null; });
			prep = { key: key, promise: p };
			return p;
		}

		form.addEventListener('click', function (e) {
			var t = e.target.closest('[data-next],[data-back]');
			if (!t) return;
			e.preventDefault();
			if (t.hasAttribute('data-back')) return show(Math.max(0, cur - 1));
			var msg = validate(cur); if (msg) return say(msg);
			if (!started) { started = true; track('jade_funnel_start'); }
			if (STEPS[cur] === 'time') prepare();
			personalize(STEPS[cur]);
			show(Math.min(STEPS.length - 1, cur + 1));
		});
		form.addEventListener('submit', function (e) {
			e.preventDefault();
			for (var i = 0; i < STEPS.length; i++) { var msg = validate(i); if (msg) { show(i); return say(msg); } }
			var data = attribution(), b = birthFields();
			Object.keys(b).forEach(function (k) { data[k] = b[k]; });
			var f = fields(form);
			['first_name', 'last_name', 'gender', 'tradition', 'topics', 'website'].forEach(function (k) { data[k] = f[k]; });
			data.topic = root.dataset.topic || 'general'; data.focus = root.dataset.focus || ''; data.source_page = root.dataset.source || '';
			data.hv = root.dataset.hv || ''; data.intent = root.dataset.intent || 'general'; data.when = root.dataset.when || 'today';

			//#wait:begin  the waiting screen: "Reading your chart…", true steps, and the reading shows only when Claude's version is ready (or after 40 seconds, with the code text)
			form.hidden = true; calc.hidden = false;
			var begun = Date.now(), tt = timeText();
			var steps = waitScreen(calc, ['Placing your planets', 'Reading your Moon and birth star', 'Mapping your life chapters', 'Writing your reading'], 'Reading your chart…',
				'Placing the planets over ' + (city() || 'your birthplace') + (tt ? (tt.indexOf('around') === 0 ? ', ' + tt : ' at ' + tt) : '') + ', ' + dateText() + '…');
			var minWait = new Promise(function (r) { setTimeout(r, 2900); });
			var prepared = (prep && prep.key === JSON.stringify(b)) ? prep.promise : Promise.resolve(null);
			var req = prepared.then(function (pr) { if (pr && pr.success && pr.data.token) data.token = pr.data.token; return api('reading', data); });
			Promise.all([req, minWait]).then(function (out) {
				var res = out[0];
				if (!res || !res.success) {
					steps.stop(); calc.hidden = true; form.hidden = false;
					var step = res && res.data && res.data.step ? STEPS.indexOf(res.data.step) : -1;
					show(step >= 0 ? step : STEPS.length - 1);
					return say((res && res.data && res.data.message) || 'Something went wrong. Please try again.');
				}
				track('jade_reading', { rarity: res.data.rarity || 0, headline: root.dataset.hv || '' });
				return finishReading(root, result, res.data, begun, steps, calc);
			}).catch(function () { steps.stop(); calc.hidden = true; form.hidden = false; say('Connection problem. Please try again.'); });
			//#wait:end
		});
		show(0);
	}

	//#wait:begin
	/* `parts` given: the reading is shown with Claude's text already in place (or, for {} , with the code text everywhere). Not given: the code text first and Claude's text swapped in later (startAI). */
	function showResult(root, result, d, parts) {
		root.classList.add('has-result');
		var head = root.querySelector('.jf-head'); if (head) head.hidden = true;
		root.querySelector('.jf-box').hidden = true;
		result.innerHTML = d.html; // built by our own brain from trusted templates
		bindReading(result);
		if (parts) fillAI(d.token, parts, true); else if (d.ai) startAI(d.token);
		result.scrollIntoView({ behavior: 'smooth', block: 'start' });
	}

	/* ---------- Parts of the reading written by Claude ---------- */
	var aiJobs = {};
	var AI_WAIT_MS = 60000, AI_GAP_MS = 2000, AI_RETRY_GAP_MS = 3000, AI_MAX_FAILS = 5, AI_FIRST_WAIT_MS = 40000;
	/* The brain writes the parts in rounds: each poll answers {pending:true} until the last round, then {parts:{slot: html}}. We keep asking for up to `ms` milliseconds in all (a poll can itself take
	   5 to 8 seconds), and a poll that fails (a dropped connection, a 5xx, a slow answer) is simply asked again after 3 seconds; only 5 failures in a row, `ms` running out or ctl.stopped end it.
	   Answers with the parts (an object, maybe empty), or null when nothing came. */
	function waitAI(token, ms, ctl) {
		var t0 = Date.now(), fails = 0;
		function ask() {
			return api('ai', { token: token }).catch(function () { return null; }).then(function (res) {
				var d = res && res.success && res.data;
				if (d && d.parts) return d.parts;                       // finished (it may be empty: then every card keeps its first text)
				if (d && !d.pending) return null;                       // an answer with nothing to wait for
				fails = d ? 0 : fails + 1;
				if (fails >= AI_MAX_FAILS || Date.now() - t0 >= ms || (ctl && ctl.stopped)) return null;
				return new Promise(function (r) { setTimeout(r, d ? AI_GAP_MS : AI_RETRY_GAP_MS); }).then(ask);
			});
		}
		return ask();
	}
	/* Used when a reading is already on the page (after the email unlock) and Claude's text may still be on its way: swapped in when it arrives, for up to 60 seconds. */
	function startAI(token) {
		if (!token || aiJobs[token]) return;
		aiJobs[token] = waitAI(token, AI_WAIT_MS).then(function (parts) { fillAI(token, parts || {}); }).catch(function () {}).then(function () { aiJobs[token] = null; });
	}
	/* Every finished card is swapped in; a card with no part (Claude's text for it was not good enough, or time ran out) keeps its first text and stops looking like it is waiting. */
	function fillAI(token, parts, quiet) {
		document.querySelectorAll('[data-jade-reading][data-token="' + token + '"] [data-ai-slot]').forEach(function (slot) {
			if (!slot.classList.contains('is-loading')) return;
			var n = slot.getAttribute('data-ai-slot');
			if (typeof parts[n] === 'string' && parts[n]) {
				slot.querySelector('.jr-ai__body').innerHTML = parts[n];
				slot.classList.remove('is-loading'); slot.classList.add('is-ready'); if (!quiet) slot.classList.add('is-new');
			} else {
				slot.classList.remove('is-loading'); slot.classList.add('is-ready');
			}
		});
	}

	/* ---------- The waiting screen ---------- */
	/* Shows the title, one line of detail and the steps. The steps are true: while the brain is calculating the chart (planets, Moon and birth star, the life chapters) they move on every 1.5 seconds
	   but never past "Mapping your life chapters"; "Writing your reading" is lit only once the brain has said that Claude is writing, and everything is ticked only when the reading is about to appear. */
	function waitScreen(calc, labels, title, sub) {
		var ul = calc.querySelector('ul');
		if (!ul) { ul = document.createElement('ul'); calc.appendChild(ul); }          // a page whose waiting box has no list gets one
		function line(cls, text) {
			var el = calc.querySelector('.' + cls);
			if (!el) { el = document.createElement('p'); el.className = cls; calc.insertBefore(el, ul); }
			el.textContent = text;
		}
		line('jf-calc__title', title);
		line('jf-calc__sub', sub || '');
		ul.textContent = '';
		var items = labels.map(function (l) { var li = document.createElement('li'); li.textContent = l; ul.appendChild(li); return li; });
		var at = 0, timer = null;
		function paint(n) { items.forEach(function (li, k) { li.classList.toggle('is-done', k < n); li.classList.toggle('is-active', k === n); }); at = n; }
		paint(0);
		timer = setInterval(function () { if (at < items.length - 2) paint(at + 1); }, 1500);
		return {
			writing: function (note) { clearInterval(timer); paint(items.length - 1); if (note) line('jf-calc__sub', note); },
			done: function () { clearInterval(timer); paint(items.length); },
			stop: function () { clearInterval(timer); }
		};
	}
	/* The reading is ready to show. With Claude's text: wait here (at most 40 seconds from the moment the person pressed the button) for it, then show the reading with that text already in place. If it is
	   not ready in time, or fails, show the reading with the code text; no error is shown and nothing changes on the page later. */
	function finishReading(root, result, d, begun, steps, calc) {
		var shown = false;
		function reveal(parts) {
			if (shown) return; shown = true;
			steps.done();
			setTimeout(function () { calc.hidden = true; showResult(root, result, d, parts); }, 450);
		}
		if (!d.ai || !d.token) { reveal(undefined); return; }
		var left = AI_FIRST_WAIT_MS - (Date.now() - begun);
		if (left <= 0) { reveal({}); return; }
		steps.writing('Your reading is being written for you. This usually takes under half a minute.');
		var ctl = { stopped: false };
		setTimeout(function () { ctl.stopped = true; reveal({}); }, left);
		waitAI(d.token, left, ctl).then(function (parts) { ctl.stopped = true; reveal(parts || {}); }).catch(function () { ctl.stopped = true; reveal({}); });
	}
	//#wait:end
	function bindReading(scope) {
		var reading = scope.querySelector('[data-jade-reading]');
		if (!reading) return;
		var token = reading.dataset.token;
		reading.querySelectorAll('[data-jade-reveal]').forEach(function (btn) {
			btn.addEventListener('click', function () {
				var slot = reading.querySelector('[data-ai-slot="' + btn.getAttribute('data-jade-reveal') + '"]');
				if (!slot) return;
				slot.hidden = false; btn.parentNode.hidden = true;
				track('jade_reveal_' + btn.getAttribute('data-jade-reveal'));
				slot.scrollIntoView({ behavior: 'smooth', block: 'start' });
			});
		});
		reading.querySelectorAll('[data-jade-capture]').forEach(function (cap) {
			cap.addEventListener('submit', function (e) {
				e.preventDefault(); showError(cap, '');
				var email = q(cap, 'email');
				if (!email.value || !email.checkValidity()) return showError(cap, 'Please enter a valid email address.');
				if (!q(cap, 'consent').checked) return showError(cap, 'Please tick the box so we can email your reading.');
				setBusy(cap, true, 'Unlocking…');
				var data = fields(cap); data.token = token;
				api('capture', data).then(function (res) {
					setBusy(cap, false);
					if (!res || !res.success) return showError(cap, (res && res.data && res.data.message) || 'Something went wrong. Please try again.');
					track('jade_optin', { method: 'reading_unlock' });
					var wrap = document.createElement('div'); wrap.innerHTML = res.data.html;
					var fresh = wrap.firstElementChild;
					reading.parentNode.replaceChild(fresh, reading);
					bindReading(fresh.parentNode);
					if (fresh.querySelector('[data-ai-slot].is-loading')) startAI(token);
					(fresh.querySelector('.jr-next') || fresh).scrollIntoView({ behavior: 'smooth', block: 'start' });
				}).catch(function () { setBusy(cap, false); showError(cap, 'Connection problem. Please try again.'); });
			});
		});
		reading.querySelectorAll('[data-jade-buy]').forEach(function (a) {
			a.addEventListener('click', function () { track('jade_buy_open', { offer: a.getAttribute('data-jade-buy') }); });
		});
		var share = reading.querySelector('[data-jade-share]');
		if (share) share.addEventListener('click', function () {
			var r = reading.dataset.rarity;
			var text = r ? 'My birth chart is about ' + r + ' births. Find out how rare yours is:' : 'I just got my free birth chart reading. See how rare yours is:';
			var url = location.origin + '/';
			track('jade_share');
			if (navigator.share) { navigator.share({ title: CFG.brand, text: text, url: url }).catch(function () {}); return; }
			var done = function () { share.textContent = 'Link copied. Paste it to a friend!'; };
			if (navigator.clipboard) navigator.clipboard.writeText(text + ' ' + url).then(done, function () { window.prompt('Copy this link:', url); });
			else window.prompt('Copy this link:', url);
		});
	}

	/* ---------- Compatibility calculator ---------- */
	function compat(root) {
		var form = root.querySelector('.jc-form');
		var calc = root.querySelector('.jf-calc'), result = root.querySelector('.jf-result');
		['a_', 'b_'].forEach(function (p) { placeAutocomplete(form, p); });
		form.querySelectorAll('[data-jade-exact]').forEach(function (b) { exactPlace(b, form); });
		form.querySelectorAll('[name$="time_unknown"]').forEach(function (cb) {
			cb.addEventListener('change', function () { var t = q(form, cb.name.slice(0, 2) + 'birth_time'); t.disabled = cb.checked; if (cb.checked) t.value = ''; });
		});
		form.addEventListener('submit', function (e) {
			e.preventDefault(); showError(form, '');
			var who = { a_: 'your', b_: 'their' };
			var ps = ['a_', 'b_'];
			for (var i = 0; i < ps.length; i++) {
				var p = ps[i];
				if (!q(form, p + 'name').value.trim()) return showError(form, 'Please enter ' + who[p] + ' first name.');
				var dv = dateValueOf(form, p);
				if (!dv || dv === 'bad') return showError(form, 'Please check ' + who[p] + ' date of birth.');
				if (!q(form, p + 'time_unknown').checked && !q(form, p + 'birth_time').value) return showError(form, 'Please enter ' + who[p] + ' birth time, or tick that it isn’t known.');
				if (!hasPlace(form, p)) return showError(form, 'Please enter ' + who[p] + ' city of birth.');
			}
			if (!q(form, 'partner_ok').checked) return showError(form, 'Please confirm you have their permission to use their birth details.');
			var data = attribution(), f = fields(form);
			Object.keys(f).forEach(function (k) { data[k] = f[k]; });
			data.a_birth_date = dateValueOf(form, 'a_'); data.b_birth_date = dateValueOf(form, 'b_');
			data.intent = root.dataset.intent || 'compat';
			//#wait:begin  the same waiting screen for the compatibility result
			form.hidden = true; calc.hidden = false;
			var begun = Date.now();
			var steps = waitScreen(calc, ['Placing both sets of planets', 'Comparing your two Moons and birth stars', 'Scoring the 36-point match', 'Writing your reading'], 'Reading your two charts…', '');
			var minWait = new Promise(function (r) { setTimeout(r, 2500); });
			Promise.all([api('compatibility', data), minWait]).then(function (out) {
				var res = out[0];
				if (!res || !res.success) { steps.stop(); calc.hidden = true; form.hidden = false; return showError(form, (res && res.data && res.data.message) || 'Something went wrong. Please try again.'); }
				track('jade_compat', { score: res.data.score || 0 });
				return finishReading(root, result, res.data, begun, steps, calc);
			}).catch(function () { steps.stop(); calc.hidden = true; form.hidden = false; showError(form, 'Connection problem. Please try again.'); });
			//#wait:end
		});
	}

	/* ---------- Checkout ---------- */
	function money(n) { return '$' + Number(n).toFixed(2).replace(/\.00$/, ''); }
	function checkout(root) {
		var p = new URLSearchParams(location.search), token = p.get('t') || '', offer = p.get('o') || 'main';
		var form = root.querySelector('.jade-co__form'), loading = root.querySelector('[data-co-loading]');
		var agreeRow = root.querySelector('[data-co-agree]'), need = root.querySelector('[data-co-need]');
		var agree = q(form, 'agree'), bump = q(form, 'bump'), offerData = null;
		function total() { return offerData.lines.reduce(function (s, l) { return s + l.price; }, 0) + (offerData.bump && bump.checked ? offerData.bump.price : 0); }
		function render() { root.querySelector('[data-co-total]').textContent = money(total()); }
		api('offer', { token: token, offer: offer }).then(function (res) {
			if (!res || !res.success) { loading.innerHTML = ''; var m = document.createElement('p'); m.className = 'jade-notice'; m.textContent = (res && res.data && res.data.message) || 'This checkout link has expired. Please start again from your reading.'; loading.appendChild(m); return; }
			offerData = res.data;
			var ul = root.querySelector('[data-co-lines]');
			offerData.lines.forEach(function (l) {
				var li = document.createElement('li'), n = document.createElement('span'), pr = document.createElement('strong');
				n.textContent = l.name; pr.textContent = money(l.price); li.appendChild(n); li.appendChild(pr); ul.appendChild(li);
			});
			if (offerData.bump) {
				root.querySelector('[data-co-bump]').hidden = false;
				root.querySelector('[data-co-bump-text]').textContent = 'Add ' + offerData.bump.name + ' for ' + money(offerData.bump.price) + (offerData.bump.blurb ? ': ' + offerData.bump.blurb : '');
			}
			if (offerData.email) q(form, 'email').value = offerData.email;
			loading.hidden = true; form.hidden = false; render();
			track('begin_checkout', { value: total(), currency: 'USD' });
		}).catch(function () { loading.textContent = 'Connection problem. Please refresh the page.'; });
		bump.addEventListener('change', render);
		agree.addEventListener('change', function () { if (agree.checked) { agreeRow.classList.remove('is-missing'); need.hidden = true; } });
		form.addEventListener('submit', function (e) {
			e.preventDefault(); showError(form, '');
			var em = q(form, 'email');
			if (!em.value || !em.checkValidity()) { em.focus(); return showError(form, 'Please enter the email where we should send your report.'); }
			if (!agree.checked) {
				agreeRow.classList.add('is-missing'); need.hidden = false;
				agreeRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
				try { agree.focus({ preventScroll: true }); } catch (x) {}
				track('jade_checkout_unticked');
				return;
			}
			setBusy(form, true, 'Opening secure payment…');
			api('checkout', {
				token: token, offer: offer, email: em.value.trim(), bump: bump.checked ? 1 : 0, agree: 1,
				agree_text: agreeRow.textContent.replace(/\s+/g, ' ').trim(), device_info: deviceInfo(), variant: offerData.variant || '', attribution: attribution()
			}).then(function (res) {
				if (!res || !res.success) { setBusy(form, false); return showError(form, (res && res.data && res.data.message) || 'Something went wrong. Please try again.'); }
				location.href = res.data.url;
			}).catch(function () { setBusy(form, false); showError(form, 'Connection problem. Please try again.'); });
		});
	}

	/* ---------- Thank-you page: order confirmation, then the offers in this buyer's order ---------- */
	function thanks(root) {
		var p = new URLSearchParams(location.search), order = p.get('order') || p.get('o') || '';
		var box = root.querySelector('[data-jade-offers]');
		api('order', { order: order }).then(function (res) {
			root.querySelector('[data-th-loading]').hidden = true;
			if (!res || !res.success) { var m = document.createElement('p'); m.textContent = 'Your payment went through. Your confirmation email is on its way.'; root.querySelector('[data-th-loading]').parentNode.insertBefore(m, box); return; }
			var d = res.data;
			root.querySelector('[data-th-order]').hidden = false;
			root.querySelector('[data-th-summary]').textContent = d.summary || '';
			root.querySelector('[data-th-email]').textContent = d.email || 'your email';
			try { var k = 'jade_paid_' + d.order; if (!localStorage.getItem(k)) { localStorage.setItem(k, '1'); track('purchase', { transaction_id: d.order, value: d.value, currency: 'USD' }); } } catch (e) {}
			offerSequence(box, d.session, d.offers || []);
		});
	}
	function offerSequence(box, session, offers) {
		var i = 0;
		function showNext() {
			box.innerHTML = '';
			if (i >= offers.length) { box.hidden = true; return; }
			var o = offers[i];
			var wrap = document.createElement('div');
			var h = document.createElement('h2'); h.textContent = o.title; wrap.appendChild(h);
			if (o.blurb) { var b = document.createElement('p'); b.textContent = o.blurb; wrap.appendChild(b); }
			if (o.points && o.points.length) { var ul = document.createElement('ul'); ul.className = 'jade-offer__list'; o.points.forEach(function (t) { var li = document.createElement('li'); li.textContent = t; ul.appendChild(li); }); wrap.appendChild(ul); }
			var price = document.createElement('p'); price.className = 'jade-offer__price'; price.textContent = money(o.price) + ' · one click, no need to re-enter your card'; wrap.appendChild(price);
			var yes = document.createElement('button'); yes.type = 'button'; yes.className = 'jade-btn jade-btn--gold'; yes.textContent = o.button || ('Yes, add it for ' + money(o.price));
			var no = document.createElement('button'); no.type = 'button'; no.className = 'jade-link'; no.textContent = o.decline || 'No thanks';
			var err = document.createElement('p'); err.className = 'jade-error'; err.hidden = true;
			var nav = document.createElement('div'); nav.className = 'jf-nav'; nav.appendChild(no); nav.appendChild(yes);
			wrap.appendChild(nav); wrap.appendChild(err);
			box.appendChild(wrap); box.hidden = false;
			track('jade_offer_view', { offer: o.key });
			no.addEventListener('click', function () { track('jade_offer_no', { offer: o.key }); i++; showNext(); });
			yes.addEventListener('click', function () {
				if (yes.disabled) return;
				yes.disabled = true; yes.textContent = 'Adding to your order…';
				api('upsell', { session: session, offer: o.key, device_info: deviceInfo() }).then(function (res) {
					if (res && res.success && res.data.redirect) { location.href = res.data.redirect; return; }
					if (!res || !res.success) { yes.disabled = false; yes.textContent = o.button || 'Yes, add it'; err.textContent = (res && res.data && res.data.message) || 'Something went wrong. Your report is not affected.'; err.hidden = false; return; }
					track('purchase', { transaction_id: res.data.order, value: res.data.value, currency: 'USD' });
					box.innerHTML = '';
					var ok = document.createElement('div'), t = document.createElement('h2');
					t.textContent = 'Added: ' + (res.data.title || o.title); ok.appendChild(t);
					if (res.data.partner) { var a = document.createElement('a'); a.className = 'jade-btn jade-btn--gold'; a.href = res.data.partner; a.textContent = 'Enter your partner’s details →'; ok.appendChild(a); }
					box.appendChild(ok);
				}).catch(function () { yes.disabled = false; err.textContent = 'Connection problem. Please try again.'; err.hidden = false; });
			});
		}
		showNext();
	}

	/* ---------- Partner details ---------- */
	function partnerForm(form) {
		var time = q(form, 'birth_time');
		var p = new URLSearchParams(location.search);
		q(form, 'order').value = p.get('order') || p.get('o') || '';
		placeAutocomplete(form);
		form.querySelectorAll('[data-jade-exact]').forEach(function (b) { exactPlace(b, form); });
		function sync() { var m = form.querySelector('[name="time_mode"]:checked'); time.parentNode.hidden = m && m.value === 'unknown'; }
		form.querySelectorAll('[name="time_mode"]').forEach(function (r) { r.addEventListener('change', sync); });
		sync();
		form.addEventListener('submit', function (e) {
			e.preventDefault(); showError(form, '');
			if (!q(form, 'partner_name').value.trim()) return showError(form, 'Please enter their first name.');
			if (!q(form, 'birth_date').value) return showError(form, 'Please enter their date of birth.');
			var m = form.querySelector('[name="time_mode"]:checked');
			if (m && m.value !== 'unknown' && !time.value) return showError(form, 'Please enter their birth time, or choose “I don’t know it”.');
			if (!hasPlace(form)) return showError(form, 'Please enter the city they were born in.');
			if (!q(form, 'consent').checked) return showError(form, 'Please confirm you have your partner’s permission.');
			setBusy(form, true, 'Sending…');
			api('partner', fields(form)).then(function (res) {
				setBusy(form, false);
				if (!res || !res.success) return showError(form, (res && res.data && res.data.message) || 'Something went wrong. Please try again.');
				track('jade_partner_details');
				form.hidden = true; form.parentNode.querySelector('[data-jade-partner-ok]').hidden = false;
			}).catch(function () { setBusy(form, false); showError(form, 'Connection problem. Please try again.'); });
		});
	}

	/* ---------- Refund request ---------- */
	function refundForm(form) {
		form.addEventListener('submit', function (e) {
			e.preventDefault(); showError(form, '');
			var em = q(form, 'email');
			if (!em.value || !em.checkValidity()) return showError(form, 'Please enter the email you ordered with.');
			if (q(form, 'reason').value.trim().length < 10) return showError(form, 'Please tell us what we got wrong (a sentence or two is enough).');
			setBusy(form, true, 'Sending…');
			var data = fields(form); data.device_info = deviceInfo();
			api('refund_request', data).then(function (res) {
				setBusy(form, false);
				if (!res || !res.success) return showError(form, (res && res.data && res.data.message) || 'Something went wrong. Please email us instead.');
				form.hidden = true; form.parentNode.querySelector('[data-jade-refund-ok]').hidden = false;
			}).catch(function () { setBusy(form, false); showError(form, 'Connection problem. Please try again.'); });
		});
	}

	function boot() {
		navToggle();
		attribution();
		applyKeyword();
		document.querySelectorAll('[data-jade-funnel]').forEach(funnel);
		document.querySelectorAll('[data-jade-compat]').forEach(compat);
		document.querySelectorAll('[data-jade-checkout]').forEach(checkout);
		document.querySelectorAll('[data-jade-thanks]').forEach(thanks);
		document.querySelectorAll('[data-jade-partner]').forEach(partnerForm);
		document.querySelectorAll('[data-jade-refund]').forEach(refundForm);
	}
	if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
	else boot();
})();
