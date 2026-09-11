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

  /* ---------- 10. 视频灯箱（点击播放） ----------
     标记约定（放在任意元素上）：
       data-video="assets/video/x.mp4"  → HTML5 播放本地文件
       data-embed="https://..."         → iframe 嵌入（B站 / YouTube / Vimeo）
       data-poster="..."  data-vtitle="..."  data-vsub="..."
     同页有多个时自动出现上一个 / 下一个。 */
  function initVideo() {
    var triggers = [].slice.call(doc.querySelectorAll('[data-video], [data-embed]'));
    if (!triggers.length) return;

    var box = doc.createElement('div');
    box.className = 'vlight';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    box.setAttribute('aria-label', '视频播放');
    box.innerHTML =
      '<div class="vlight__top">' +
        '<div class="vlight__meta">' +
          '<span class="vlight__title"></span>' +
          '<span class="vlight__sub"></span>' +
        '</div>' +
        '<button class="vlight__x" type="button" aria-label="关闭"><span></span></button>' +
      '</div>' +
      '<div class="vlight__stage">' +
        '<div class="vlight__frame"></div>' +
        '<div class="vlight__nav">' +
          '<button class="vlight__prev" type="button" aria-label="上一个">‹</button>' +
          '<button class="vlight__next" type="button" aria-label="下一个">›</button>' +
        '</div>' +
      '</div>' +
      '<div class="vlight__bot">' +
        '<span class="vlight__hint"><b>ESC</b> 关闭 · <b>空格</b> 播放 / 暂停 · <b>← →</b> 切换</span>' +
        '<span class="vlight__count"></span>' +
      '</div>';

    var frame   = box.querySelector('.vlight__frame');
    var elTitle = box.querySelector('.vlight__title');
    var elSub   = box.querySelector('.vlight__sub');
    var elCount = box.querySelector('.vlight__count');
    var btnX    = box.querySelector('.vlight__x');
    var btnPrev = box.querySelector('.vlight__prev');
    var btnNext = box.querySelector('.vlight__next');
    doc.body.appendChild(box);

    var media = null;      // 当前的 <video> 或 <iframe>
    var index = 0;
    var lastFocus = null;
    var idleTimer = null;

    function clearMedia() {
      if (media) {
        try { if (media.pause) media.pause(); } catch (e) {}
        media.removeAttribute('src');
        media.innerHTML = '';
        if (media.load) { try { media.load(); } catch (e) {} }
      }
      frame.innerHTML = '';
      media = null;
    }

    function buildMedia(trigger) {
      clearMedia();
      var file  = trigger.getAttribute('data-video');
      var embed = trigger.getAttribute('data-embed');

      if (embed) {
        media = doc.createElement('iframe');
        media.setAttribute('src', embed);
        media.setAttribute('allow', 'accelerometer; autoplay; clipboard-write; encrypted-media; picture-in-picture; fullscreen');
        media.setAttribute('allowfullscreen', '');
        media.setAttribute('loading', 'lazy');
        media.setAttribute('title', trigger.getAttribute('data-vtitle') || '视频');
        frame.appendChild(media);
        return;
      }

      media = doc.createElement('video');
      media.setAttribute('src', file);
      media.setAttribute('controls', '');
      media.setAttribute('playsinline', '');
      media.setAttribute('preload', 'metadata');
      var poster = trigger.getAttribute('data-poster');
      if (poster) media.setAttribute('poster', poster);
      frame.appendChild(media);
      var pr = media.play();
      if (pr && pr.catch) pr.catch(function () { /* 浏览器拦截自动播放时，显示封面等用户点播放 */ });
    }

    function armIdle() {
      box.classList.remove('is-idle');
      clearTimeout(idleTimer);
      idleTimer = setTimeout(function () {
        if (box.classList.contains('is-open') && media && media.tagName === 'VIDEO' && !media.paused) {
          box.classList.add('is-idle');
        }
      }, 2800);
    }

    function show(i) {
      index = (i + triggers.length) % triggers.length;
      var trig = triggers[index];
      elTitle.textContent = trig.getAttribute('data-vtitle') || '视频案例';
      elSub.textContent   = trig.getAttribute('data-vsub') || '';
      elCount.textContent = triggers.length > 1
        ? ('0' + (index + 1)).slice(-2) + ' / ' + ('0' + triggers.length).slice(-2)
        : '';
      btnPrev.hidden = btnNext.hidden = triggers.length < 2;
      buildMedia(trig);
      armIdle();
    }

    function open(i) {
      lastFocus = doc.activeElement;
      show(i);
      box.classList.add('is-open');
      root.classList.add('is-locked');
      btnX.focus({ preventScroll: true });
    }

    function close() {
      box.classList.remove('is-open', 'is-idle');
      root.classList.remove('is-locked');
      clearTimeout(idleTimer);
      clearMedia();
      if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
    }

    function isOpen() { return box.classList.contains('is-open'); }

    triggers.forEach(function (trig, i) {
      trig.addEventListener('click', function (e) {
        e.preventDefault();
        open(i);
      });
    });

    btnX.addEventListener('click', close);
    btnPrev.addEventListener('click', function () { show(index - 1); });
    btnNext.addEventListener('click', function () { show(index + 1); });
    box.addEventListener('click', function (e) { if (e.target === box) close(); });
    box.addEventListener('mousemove', armIdle);
    box.addEventListener('touchstart', armIdle, { passive: true });

    doc.addEventListener('keydown', function (e) {
      if (!isOpen()) return;
      if (e.key === 'Escape') { e.preventDefault(); close(); }
      else if (e.key === 'ArrowLeft'  && triggers.length > 1) { show(index - 1); }
      else if (e.key === 'ArrowRight' && triggers.length > 1) { show(index + 1); }
      else if (e.key === ' ' && media && media.tagName === 'VIDEO') {
        e.preventDefault();
        if (media.paused) media.play(); else media.pause();
      }
      armIdle();
    });
  }

  /* ---------- 11. 案例页目录高亮（滚动到哪一节） ---------- */
  function initCaseToc() {
    var links = [].slice.call(doc.querySelectorAll('.ctoc a[href^="#"]'));
    if (!links.length || !('IntersectionObserver' in window)) return;
    var map = {};
    links.forEach(function (a) {
      var t = doc.querySelector(a.getAttribute('href'));
      if (t) map[t.id] = a;
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var a = map[en.target.id];
        if (!a) return;
        if (en.isIntersecting) {
          links.forEach(function (x) { x.style.color = ''; });
          a.style.color = 'var(--fg)';
        }
      });
    }, { rootMargin: '-96px 0px -60% 0px' });
    Object.keys(map).forEach(function (id) { io.observe(doc.getElementById(id)); });
  }

  /* ---------- 12. 杂项 ---------- */
  function initMisc() {
    var y = doc.querySelector('[data-year]');
    if (y) y.textContent = new Date().getFullYear();

    // 图片懒加载兜底
    [].slice.call(doc.querySelectorAll('img')).forEach(function (img) {
      if (!img.getAttribute('loading')) img.setAttribute('loading', 'lazy');
      if (!img.getAttribute('decoding')) img.setAttribute('decoding', 'async');
    });
  }

  /* ---------- 13. 邮箱反爬（base64 重组） ---------- */
  function initMailGuard() {
    [].slice.call(doc.querySelectorAll('[data-mail]')).forEach(function (a) {
      var mail = '';
      try { mail = atob(a.getAttribute('data-mail')); } catch (e) { return; }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(mail)) return;
      a.textContent = mail;
      a.setAttribute('href', 'mailto:' + mail);
    });
  }

  /* ---------- 14. 微信一键复制 ---------- */
  function initWxCopy() {
    [].slice.call(doc.querySelectorAll('[data-copywx]')).forEach(function (btn) {
      if (btn.dataset.wxInit) return;
      btn.dataset.wxInit = '1';
      btn.addEventListener('click', function () {
        var wx = btn.getAttribute('data-copywx');
        function done() {
          btn.classList.add('is-copied');
          clearTimeout(btn._wxT);
          btn._wxT = setTimeout(function () { btn.classList.remove('is-copied'); }, 1800);
        }
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(wx).then(done, function () { legacy(); });
        } else { legacy(); }
        function legacy() {
          var ta = doc.createElement('textarea');
          ta.value = wx;
          ta.style.cssText = 'position:fixed;opacity:0;pointer-events:none';
          doc.body.appendChild(ta);
          ta.select();
          try { doc.execCommand('copy'); done(); } catch (e) {}
          ta.parentNode.removeChild(ta);
        }
      });
    });
  }

  /* ---------- 15. Hero 视频背景（可见才播，省流量） ---------- */
  function initHeroVideo() {
    var v = doc.querySelector('.hero__video');
    if (!v || v.dataset.heroInit) return;
    v.dataset.heroInit = '1';
    v.setAttribute('muted', '');
    v.setAttribute('playsinline', '');
    // 尊重 reduced-motion：不自动播放
    var mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (mq.matches) { v.removeAttribute('autoplay'); return; }
    // 页签隐藏时暂停
    doc.addEventListener('visibilitychange', function () {
      if (doc.hidden) { v.pause(); }
      else { v.play().catch(function () {}); }
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { v.play().catch(function () {}); }
        else { v.pause(); }
      });
    }, { threshold: 0.05 });
    io.observe(v);
  }

  /* ---------- 启动 ---------- */
  function ready(fn) {
    if (doc.readyState !== 'loading') fn();
    else doc.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {
    root.classList.add('js');
    collectNavZones();
    Reveal.init();
    initPeek();
    initMenu();
    initCounters();
    initFilters();
    initAnchors();
    initVideo();
    initCaseToc();
    initMailGuard();
    initWxCopy();
    initHeroVideo();
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
