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

  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* phone bar and the consultation tab: after the first screen, out of the way at the very end */
  var bar = document.querySelector('.callbar'), tab = document.querySelector('.tab');
  var tick = function () {
    var y = scrollY, end = document.documentElement.scrollHeight - innerHeight - y;
    if (bar) bar.classList.toggle('is-on', y > innerHeight * 0.55 && end > 420);
    if (tab) tab.classList.toggle('is-on', y > innerHeight * 0.4 && end > 360);
  };
  addEventListener('scroll', tick, { passive: true }); addEventListener('resize', tick); tick();

  /* hairlines draw in once, like the rule under the wordmark */
  var hls = [].slice.call(document.querySelectorAll('.hl'));
  if (reduce || !('IntersectionObserver' in window)) hls.forEach(function (el) { el.classList.add('in'); });
  else {
    var hio = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting || en.boundingClientRect.top < 0) { en.target.classList.add('in'); hio.unobserve(en.target); } }); }, { rootMargin: '0px 0px -8% 0px' });
    hls.forEach(function (el) { hio.observe(el); });
    addEventListener('beforeprint', function () { hls.forEach(function (el) { el.classList.add('in'); }); });
  }

  /* hero photograph drifts slower than the page and eases in a touch (desktop, fine pointer) */
  var heroPic = document.querySelector('.hero picture');
  if (heroPic && fine && !reduce && innerWidth >= 900) {
    var hero = heroPic.closest('.hero'), ticking = false;
    var drift = function () {
      ticking = false;
      var h = hero.offsetHeight, y = Math.min(Math.max(scrollY, 0), h);
      heroPic.style.transform = 'translate3d(0,' + (y * 0.22).toFixed(1) + 'px,0) scale(' + (1 + (y / h) * 0.05).toFixed(4) + ')';
    };
    addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(drift); } }, { passive: true });
    drift();
  }

  /* phone: legal sections fold into tap-to-open rows */
  var prose = document.querySelector('.prose:not(.prose--one)');
  if (prose && matchMedia('(max-width: 759px)').matches) {
    [].slice.call(prose.querySelectorAll(':scope > h2')).forEach(function (h) {
      var d = document.createElement('details'), sm = document.createElement('summary'), body = h.nextElementSibling;
      d.className = 'more-fields'; sm.textContent = h.textContent; d.appendChild(sm);
      if (body && body.tagName === 'P') d.appendChild(body);
      h.replaceWith(d);
    });
  }

  /* phone: optional form fields start folded */
  var fold = document.querySelector('[data-fold]');
  if (fold && matchMedia('(max-width: 759px)').matches) fold.open = false;

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
