/* signature-web · base/motion.js (from the AKMIRA reference build, 2026-10-01)
   Studio motion as behaviour only; the look stays per client.
   Markup hooks: [data-nav] header, [data-hero] first screen, .rv text/UI blocks (never photos),
   [data-par="4"] wrapper around a framed photo (amplitude in percent), .intro overlay with .intro__mark,
   [data-menu], [data-menu-open], [data-menu-close], gallery: [data-lb] dialog, [data-open="key"][data-index],
   window.GALLERY = { key: [{src,w,h}] }, window.GALLERY_TITLES = { key: 'Title · Place' }.
   Load lenis.min.js before this file (defer both). In <head>, before any CSS paints:
   <script>(function(d){d.classList.add('js');var r=matchMedia('(prefers-reduced-motion: reduce)').matches,s;try{s=sessionStorage.getItem('intro-seen')}catch(e){}if(r||s)d.classList.add('no-intro')})(document.documentElement)</script>
   Without the .intro element the page simply skips it. */
(function () {
  var root = document.documentElement;
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = matchMedia('(hover: hover) and (pointer: fine)').matches;
  var nav = document.querySelector('[data-nav]');
  var hero = document.querySelector('[data-hero]');
  var hasIntro = !!document.querySelector('.intro');
  if (!hasIntro) root.classList.add('no-intro');

  /* smooth scroll: wheel only, touch stays native */
  var lenis = null;
  if (!reduce && window.Lenis) {
    lenis = new Lenis({ lerp: 0.1, smoothWheel: true });
    var raf = function (t) { lenis.raf(t); requestAnimationFrame(raf); };
    requestAnimationFrame(raf);
  }
  var navH = function () { return nav ? nav.offsetHeight : 0; };
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href^="#"]'); if (!a) return;
    var id = a.getAttribute('href'); if (id.length < 2) return;
    var t = document.querySelector(id); if (!t) return;
    e.preventDefault();
    var off = (hero && t === hero) ? 0 : -navH() + 1;
    if (lenis) lenis.scrollTo(t, { offset: off, duration: 1.4 }); else window.scrollTo({ top: t.getBoundingClientRect().top + scrollY + off, behavior: reduce ? 'auto' : 'smooth' });
  });

  /* reveals: text and UI only, once; the hero waits for the intro */
  var els = [].slice.call(document.querySelectorAll('.rv'));
  var heroEls = els.filter(function (el) { return hero && hero.contains(el); });
  var restEls = els.filter(function (el) { return heroEls.indexOf(el) < 0; });
  var show = function (el) { el.classList.add('in'); };
  if (reduce || !('IntersectionObserver' in window)) { els.forEach(show); }
  else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting || e.boundingClientRect.top < 0) { show(e.target); io.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    restEls.forEach(function (el) { io.observe(el); });
    var sweep = function () { restEls.forEach(function (el) { var r = el.getBoundingClientRect(); if (r.top < innerHeight && r.bottom > 0) show(el); }); };
    setTimeout(sweep, 3200);
    addEventListener('pageshow', sweep);
    addEventListener('beforeprint', function () { els.forEach(show); });
  }

  /* intro: the client's mark once per session, then the hero settles */
  var ready = function () {
    root.classList.add('is-ready');
    setTimeout(function () { heroEls.forEach(show); }, root.classList.contains('no-intro') ? 120 : 380);
    try { sessionStorage.setItem('intro-seen', '1'); } catch (e) {}
  };
  var fontsReady = (document.fonts && document.fonts.ready) ? document.fonts.ready : Promise.resolve();
  if (root.classList.contains('no-intro')) { fontsReady.then(function () { requestAnimationFrame(ready); }); }
  else {
    if (lenis) lenis.stop();
    var t0 = Date.now();
    Promise.race([fontsReady, new Promise(function (r) { setTimeout(r, 2000); })]).then(function () {
      setTimeout(function () { ready(); if (lenis) lenis.start(); }, Math.max(0, 1250 - (Date.now() - t0)));
    });
  }
  setTimeout(function () { if (!root.classList.contains('is-ready')) { ready(); if (lenis) lenis.start(); } }, 3500);

  /* parallax inside the frame: desktop with a fine pointer only */
  var pars = [].slice.call(document.querySelectorAll('[data-par]'));
  var parOn = !reduce && finePointer && innerWidth >= 1024 && pars.length;
  var updatePar = function () {
    var vh = innerHeight;
    for (var i = 0; i < pars.length; i++) {
      var el = pars[i], box = el.parentElement.getBoundingClientRect();
      if (box.bottom < -100 || box.top > vh + 100) continue;
      var p = ((box.top + box.height / 2) - vh / 2) / (vh / 2 + box.height / 2);
      el.style.setProperty('--py', (-p * (+(el.getAttribute('data-par') || 4))).toFixed(3) + '%');
    }
  };
  if (parOn) { root.classList.add('has-par'); updatePar(); }

  /* nav: solid after the hero, steps away while reading down, returns on the way up */
  var lastY = scrollY, menuOpen = false;
  var onScroll = function (y) {
    if (parOn) updatePar();
    if (!nav) return;
    nav.classList.toggle('is-solid', hero ? hero.getBoundingClientRect().bottom <= navH() + 1 : true);
    var dy = y - lastY;
    if (!menuOpen && !reduce) {
      if (y > innerHeight * 0.9 && dy > 4) nav.classList.add('is-away');
      else if (dy < -4 || y < innerHeight * 0.5) nav.classList.remove('is-away');
    }
    lastY = y;
  };
  if (lenis) lenis.on('scroll', function (l) { onScroll(l.scroll); });
  else addEventListener('scroll', function () { onScroll(scrollY); }, { passive: true });
  addEventListener('resize', function () { onScroll(scrollY); });
  onScroll(scrollY);
  nav && nav.addEventListener('focusin', function () { nav.classList.remove('is-away'); });

  /* menu */
  var menu = document.querySelector('[data-menu]');
  var openBtn = document.querySelector('[data-menu-open]');
  var setMenu = function (open) {
    if (!menu) return;
    menuOpen = open; menu.hidden = !open;
    openBtn && openBtn.setAttribute('aria-expanded', String(open));
    if (lenis) { open ? lenis.stop() : lenis.start(); } else document.body.style.overflow = open ? 'hidden' : '';
    if (open) { var first = menu.querySelector('a'); first && first.focus(); } else { openBtn && openBtn.focus(); }
  };
  openBtn && openBtn.addEventListener('click', function () { setMenu(true); });
  menu && menu.addEventListener('click', function (e) { if (e.target.closest('[data-menu-close]')) setMenu(false); });
  addEventListener('keydown', function (e) { if (e.key === 'Escape' && menu && !menu.hidden) setMenu(false); });

  /* gallery */
  var G = window.GALLERY || {}, titles = window.GALLERY_TITLES || {};
  var lb = document.querySelector('[data-lb]');
  if (!lb || typeof lb.showModal !== 'function') return;
  var img = lb.querySelector('[data-lb-img]'), tEl = lb.querySelector('[data-lb-title]'), cEl = lb.querySelector('[data-lb-count]');
  var cur = { key: null, i: 0 };
  var render = function () {
    var list = G[cur.key] || []; if (!list.length) return;
    var it = list[cur.i];
    img.classList.add('is-loading');
    var pre = new Image(); pre.onload = pre.onerror = function () { img.src = it.src; img.width = it.w; img.height = it.h; img.classList.remove('is-loading'); };
    pre.src = it.src;
    img.alt = (titles[cur.key] || '') + ', ' + (cur.i + 1) + ' / ' + list.length;
    if (tEl) tEl.textContent = titles[cur.key] || '';
    if (cEl) cEl.textContent = (cur.i + 1) + ' / ' + list.length;
    var nx = list[(cur.i + 1) % list.length]; if (nx) { var p2 = new Image(); p2.src = nx.src; }
  };
  var go = function (d) { var n = (G[cur.key] || []).length; if (!n) return; cur.i = (cur.i + d + n) % n; render(); };
  document.addEventListener('click', function (e) {
    var a = e.target.closest('[data-open]'); if (!a) return;
    var key = a.getAttribute('data-open'); if (!G[key]) return;
    e.preventDefault(); cur.key = key; cur.i = +a.getAttribute('data-index') || 0; render();
    lb.showModal(); if (lenis) lenis.stop(); else document.body.style.overflow = 'hidden';
  });
  var q = function (s) { return lb.querySelector(s); };
  q('[data-lb-prev]') && q('[data-lb-prev]').addEventListener('click', function () { go(-1); });
  q('[data-lb-next]') && q('[data-lb-next]').addEventListener('click', function () { go(1); });
  q('[data-lb-close]') && q('[data-lb-close]').addEventListener('click', function () { lb.close(); });
  lb.addEventListener('close', function () { if (lenis) lenis.start(); else document.body.style.overflow = ''; });
  lb.addEventListener('keydown', function (e) { if (e.key === 'ArrowRight') go(1); if (e.key === 'ArrowLeft') go(-1); });
  var sx = null;
  lb.addEventListener('touchstart', function (e) { sx = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener('touchend', function (e) { if (sx === null) return; var dx = e.changedTouches[0].clientX - sx; if (Math.abs(dx) > 40) go(dx < 0 ? 1 : -1); sx = null; });
})();

/* ===== Joinwell Joinery: page behaviour ===== */
(function () {
  var fine = matchMedia('(hover: hover) and (pointer: fine)').matches;

  /* index rows swap the plate (rooms on home, projects on /work/) */
  [].forEach.call(document.querySelectorAll('[data-ix]'), function (ix) {
    var rows = ix.querySelectorAll('[data-k]'), imgs = ix.querySelectorAll('.ix__plate img'), cap = ix.querySelector('.ix__cap');
    var set = function (k) {
      [].forEach.call(rows, function (r) { r.classList.toggle('is-on', r.getAttribute('data-k') === k); });
      [].forEach.call(imgs, function (im) { var on = im.getAttribute('data-k') === k; im.classList.toggle('is-on', on); if (on && cap) cap.textContent = im.getAttribute('data-cap') || ''; });
    };
    [].forEach.call(rows, function (r) {
      var k = r.getAttribute('data-k');
      r.addEventListener('focus', function () { set(k); });
      if (fine) r.addEventListener('pointerenter', function () { set(k); });
    });
  });

  /* showroom filter */
  var fl = document.querySelector('[data-filters]');
  if (fl) {
    var items = document.querySelectorAll('[data-cat]');
    fl.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      var c = b.getAttribute('data-f');
      [].forEach.call(fl.querySelectorAll('button'), function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      var n = 0;
      [].forEach.call(items, function (it) { var show = c === 'all' || (' ' + it.getAttribute('data-cat') + ' ').indexOf(' ' + c + ' ') > -1; it.hidden = !show; if (show) n++; });
      var out = document.querySelector('[data-count]'); if (out) out.textContent = n + (n === 1 ? ' photograph' : ' photographs');
    });
  }

  /* phone bar: after the first screen, out of the way at the very end */
  var bar = document.querySelector('.callbar');
  if (bar) {
    var tick = function () {
      var y = scrollY, end = document.documentElement.scrollHeight - innerHeight - y;
      bar.classList.toggle('is-on', y > innerHeight * 0.55 && end > 420);
    };
    addEventListener('scroll', tick, { passive: true }); addEventListener('resize', tick); tick();
  }

  /* enquiry form: honest states, the real endpoint */
  var f = document.querySelector('[data-enquiry]');
  if (f) {
    var nx = f.querySelector('input[name="_next"]'); if (nx) nx.value = location.origin + '/thanks/';
    var check = function (field) {
      var el = field.querySelector('input, select, textarea'); if (!el) return true;
      var ok = el.checkValidity(); var msg = field.querySelector('.msg');
      field.setAttribute('data-state', ok ? '' : 'error');
      if (msg) msg.textContent = ok ? '' : (el.validity.valueMissing ? 'Please fill this in.' : el.type === 'email' ? 'Please check the email address.' : 'Please check this.');
      if (el.type === 'file' && el.files) { var big = [].some.call(el.files, function (x) { return x.size > 5 * 1024 * 1024; }); if (big) { field.setAttribute('data-state', 'error'); if (msg) msg.textContent = 'Each photo needs to be under 5 MB.'; return false; } }
      return ok;
    };
    [].forEach.call(f.querySelectorAll('.field'), function (fd) { var el = fd.querySelector('input, select, textarea'); el && el.addEventListener('blur', function () { if (el.value) check(fd); }); });
    f.addEventListener('submit', function (e) {
      var bad = [].filter.call(f.querySelectorAll('.field'), function (fd) { return !check(fd); });
      if (bad.length) { e.preventDefault(); var first = bad[0].querySelector('input, select, textarea'); first && first.focus(); return; }
      var btn = f.querySelector('button[type="submit"]'); if (btn) { btn.disabled = true; btn.textContent = 'Sending'; }
    });
  }
})();
