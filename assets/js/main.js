/* ============================================================
   PORTFOLIO — Interactions
   ============================================================ */
(function () {
  'use strict';

  var doc = document;
  var root = doc.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  /* ---------- 1. 首屏入场 ---------- */
  function boot() {
    requestAnimationFrame(function () {
      doc.body.classList.add('is-ready');
      Reveal.flush();
    });
  }

  /* ---------- 2. 导航状态（滚动实心 + 明暗自适应） ---------- */
  var nav = doc.querySelector('.nav');
  var progressBar = doc.querySelector('.progress__bar');
  var navZones = [];

  function collectNavZones() {
    navZones = [].slice.call(doc.querySelectorAll('[data-nav]'));
  }

  var lastScroll = 0;
  function onScroll() {
    var y = window.pageYOffset || root.scrollTop;

    if (nav) {
      nav.classList.toggle('is-solid', y > 40);
    }

    // 进度条
    if (progressBar) {
      var max = (root.scrollHeight - window.innerHeight) || 1;
      progressBar.style.width = Math.min(100, Math.max(0, (y / max) * 100)) + '%';
    }

    // 导航配色跟随所在区块
    if (nav && navZones.length) {
      var probe = 34; // 导航垂直中线
      var active = null;
      for (var i = 0; i < navZones.length; i++) {
        var r = navZones[i].getBoundingClientRect();
        if (r.top <= probe && r.bottom >= probe) { active = navZones[i]; }
      }
      nav.classList.toggle('is-dark', !!(active && active.getAttribute('data-nav') === 'dark'));
    }

    lastScroll = y;
  }

  /* ---------- 3. 滚动显现 ---------- */
  var Reveal = {
    items: [],
    init: function () {
      if (reduce || !('IntersectionObserver' in window)) {
        [].slice.call(doc.querySelectorAll('.reveal, .mask-line')).forEach(function (el) {
          el.classList.add('is-in');
        });
        return;
      }
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            e.target.classList.add('is-in');
            io.unobserve(e.target);
          }
        });
      }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });
      this.items = [].slice.call(doc.querySelectorAll('.reveal, .mask-line'));
      this.items.forEach(function (el) { io.observe(el); });
    },
    flush: function () {
      // 首屏内的元素立即显现（避免等待滚动）
      this.items.forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.top < window.innerHeight * 0.92) el.classList.add('is-in');
      });
    }
  };

  /* ---------- 4. 目录悬停预览 ---------- */
  function initPeek() {
    var rows = [].slice.call(doc.querySelectorAll('[data-peek]'));
    if (!rows.length || !finePointer) return;

    var peek = doc.createElement('div');
    peek.className = 'peek';
    peek.setAttribute('aria-hidden', 'true');

    var seen = {};
    var order = [];
    rows.forEach(function (row) {
      var src = row.getAttribute('data-peek');
      if (!(src in seen)) {
        var img = doc.createElement('img');
        img.src = src;
        img.alt = '';
        img.loading = 'eager';
        peek.appendChild(img);
        seen[src] = order.length;
        order.push(src);
      }
      row.setAttribute('data-peek-idx', seen[src]);
    });
    doc.body.appendChild(peek);

    var imgs = [].slice.call(peek.children);
    var target = { x: 0, y: 0 }, cur = { x: 0, y: 0 }, raf = null;

    function loop() {
      cur.x += (target.x - cur.x) * 0.14;
      cur.y += (target.y - cur.y) * 0.14;
      peek.style.transform = 'translate(' + cur.x + 'px,' + cur.y + 'px) translate(-50%,-50%)'
        + (peek.classList.contains('is-on') ? ' scale(1)' : ' scale(.9)');
      raf = requestAnimationFrame(loop);
    }

    rows.forEach(function (row) {
      row.addEventListener('mouseenter', function () {
        var idx = +row.getAttribute('data-peek-idx');
        imgs.forEach(function (im, i) { im.classList.toggle('is-active', i === idx); });
        peek.classList.add('is-on');
      });
      row.addEventListener('mouseleave', function () {
        peek.classList.remove('is-on');
      });
    });

    doc.addEventListener('mousemove', function (e) {
      target.x = e.clientX;
      target.y = e.clientY;
    }, { passive: true });

    if (!reduce) { raf = requestAnimationFrame(loop); }
    else {
      doc.addEventListener('mousemove', function (e) {
        peek.style.transform = 'translate(' + e.clientX + 'px,' + e.clientY + 'px) translate(-50%,-50%)';
      }, { passive: true });
    }
  }

  /* ---------- 5. 全屏菜单 ---------- */
  function initMenu() {
    var toggle = doc.querySelector('.nav__toggle');
    if (!toggle) return;
    var links = [].slice.call(doc.querySelectorAll('.menu__item'));

    links.forEach(function (l, i) {
      l.style.transitionDelay = (0.06 * i + 0.12) + 's';
    });

    function set(open) {
      doc.body.classList.toggle('is-menu-open', open);
      root.classList.toggle('is-locked', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open) {
        links.forEach(function (l) { l.style.opacity = ''; });
      }
    }
    toggle.addEventListener('click', function () {
      set(!doc.body.classList.contains('is-menu-open'));
    });
    doc.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') set(false);
    });
    [].slice.call(doc.querySelectorAll('.menu a')).forEach(function (a) {
      a.addEventListener('click', function () { set(false); });
    });
  }

  /* ---------- 6. 数字滚动 ---------- */
  function initCounters() {
    var nodes = [].slice.call(doc.querySelectorAll('[data-count]'));
    if (!nodes.length) return;
    if (reduce || !('IntersectionObserver' in window)) {
      nodes.forEach(function (n) { n.textContent = n.getAttribute('data-count'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var el = e.target;
        io.unobserve(el);
        var end = parseFloat(el.getAttribute('data-count'));
        var dec = (el.getAttribute('data-dec') | 0);
        var dur = 1500, t0 = null;
        function step(t) {
          if (t0 === null) t0 = t;
          var p = Math.min(1, (t - t0) / dur);
          var eased = 1 - Math.pow(1 - p, 3);
          el.textContent = (end * eased).toFixed(dec);
          if (p < 1) requestAnimationFrame(step);
          else el.textContent = end.toFixed(dec);
        }
        requestAnimationFrame(step);
      });
    }, { threshold: 0.4 });
    nodes.forEach(function (n) { io.observe(n); });
  }

  /* ---------- 7. 作品筛选 ---------- */
  function initFilters() {
    var bar = doc.querySelector('.filters');
    if (!bar) return;
    var btns = [].slice.call(bar.querySelectorAll('button'));
    var items = [].slice.call(doc.querySelectorAll('[data-cat]'));

    btns.forEach(function (b) {
      b.addEventListener('click', function () {
        var f = b.getAttribute('data-filter');
        btns.forEach(function (x) { x.classList.toggle('is-active', x === b); });
        items.forEach(function (it) {
          var match = f === 'all' || (it.getAttribute('data-cat') || '').split(' ').indexOf(f) > -1;
          it.style.display = match ? '' : 'none';
        });
      });
    });
  }

  /* ---------- 8. 锚点平滑滚动（补偿固定导航） ---------- */
  function initAnchors() {
    [].slice.call(doc.querySelectorAll('a[href^="#"]')).forEach(function (a) {
      var id = a.getAttribute('href');
      if (id === '#' || id.length < 2) return;
      a.addEventListener('click', function (e) {
        var t = doc.querySelector(id);
        if (!t) return;
        e.preventDefault();
        var y = t.getBoundingClientRect().top + window.pageYOffset - (window.innerWidth > 880 ? 60 : 20);
        window.scrollTo({ top: y, behavior: reduce ? 'auto' : 'smooth' });
      });
    });
  }

  /* ---------- 9. 杂项 ---------- */
  function initMisc() {
    var y = doc.querySelector('[data-year]');
    if (y) y.textContent = new Date().getFullYear();

    // 图片懒加载兜底
    [].slice.call(doc.querySelectorAll('img')).forEach(function (img) {
      if (!img.getAttribute('loading')) img.setAttribute('loading', 'lazy');
      if (!img.getAttribute('decoding')) img.setAttribute('decoding', 'async');
    });
  }

  /* ---------- 启动 ---------- */
  function ready(fn) {
    if (doc.readyState !== 'loading') fn();
    else doc.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {
    collectNavZones();
    Reveal.init();
    initPeek();
    initMenu();
    initCounters();
    initFilters();
    initAnchors();
    initMisc();
    onScroll();

    var ticking = false;
    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () { onScroll(); ticking = false; });
    }, { passive: true });

    window.addEventListener('resize', function () { collectNavZones(); Reveal.flush(); });
    window.addEventListener('load', boot);
    setTimeout(boot, 400); // 兜底：避免极端情况下首屏不显现
  });
})();
