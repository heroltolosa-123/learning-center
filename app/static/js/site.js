/* Hero Academy — interaction layer.
   No framework, no build step. Everything degrades: with JS off the `.no-js`
   class keeps all revealed content visible and every control still works. */
(function () {
  'use strict';

  var root = document.documentElement;
  root.classList.remove('no-js');
  root.classList.add('js');

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');

  /* ---------------------------------------------------------------- nav ---*/
  var nav = document.querySelector('.site-nav');
  if (nav && !nav.classList.contains('is-solid')) {
    var stuck = false;
    var onScroll = function () {
      var should = window.scrollY > 8;
      if (should !== stuck) {
        stuck = should;
        nav.classList.toggle('is-stuck', stuck);
      }
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* Mobile drawer */
  var toggle = document.querySelector('.nav-toggle');
  var drawer = document.getElementById('nav-drawer');
  if (toggle && drawer) {
    var setOpen = function (open) {
      toggle.setAttribute('aria-expanded', String(open));
      drawer.classList.toggle('is-open', open);
      document.body.classList.toggle('nav-open', open);
      if (!open) { drawer.setAttribute('inert', ''); } else { drawer.removeAttribute('inert'); }
    };
    setOpen(false);

    toggle.addEventListener('click', function () {
      setOpen(toggle.getAttribute('aria-expanded') !== 'true');
    });
    drawer.addEventListener('click', function (e) {
      if (e.target.closest('a')) { setOpen(false); }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        setOpen(false);
        toggle.focus();
      }
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth >= 1000) { setOpen(false); }
    });
  }

  /* ------------------------------------------------------------ reveals ---*/
  var revealables = document.querySelectorAll('.reveal, .steps');

  if (reduced.matches || !('IntersectionObserver' in window)) {
    revealables.forEach(function (el) { el.classList.add('is-visible'); });
    document.querySelectorAll('[data-count-to]').forEach(function (el) {
      el.textContent = formatCount(el, Number(el.getAttribute('data-count-to')));
    });
    initProgressBars(true);
    return;
  }

  /* Stagger index for grouped children */
  document.querySelectorAll('.stagger').forEach(function (group) {
    Array.prototype.forEach.call(group.children, function (child, i) {
      child.style.setProperty('--i', Math.min(i, 9));
    });
  });

  /* threshold 0 + a negative bottom margin: an element reveals as soon as any of
     it crosses the trigger line. A percentage threshold is unreachable for an
     element taller than the viewport, which is common on a phone. */
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) { return; }
      entry.target.classList.add('is-visible');
      observer.unobserve(entry.target);
    });
  }, { threshold: 0, rootMargin: '0px 0px -10% 0px' });

  revealables.forEach(function (el) { observer.observe(el); });

  /* Landing straight on an anchor (/#contact from the nav, a shared link, a
     back-navigation) jumps past everything above it, and those elements would
     never receive an intersection. Show anything already scrolled past, with no
     animation to catch up on. */
  var catchUp = function () {
    revealables.forEach(function (el) {
      if (el.getBoundingClientRect().bottom < 0) {
        el.classList.add('is-visible');
        observer.unobserve(el);
      }
    });
  };
  catchUp();
  /* Anchor jumps and scroll restoration land after this script runs, so sweep
     again once the browser has settled on its final scroll position. */
  window.addEventListener('load', catchUp);

  /* ----------------------------------------------------------- counters ---*/
  function formatCount(el, value) {
    var suffix = el.getAttribute('data-count-suffix') || '';
    return String(value) + suffix;
  }

  var counters = document.querySelectorAll('[data-count-to]');
  if (counters.length) {
    var counterObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) { return; }
        var el = entry.target;
        counterObserver.unobserve(el);
        countUp(el, Number(el.getAttribute('data-count-to')));
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) {
      el.textContent = formatCount(el, 0);
      counterObserver.observe(el);
    });
  }

  function countUp(el, target) {
    var duration = 1100;
    var start = null;
    var step = function (now) {
      if (start === null) { start = now; }
      var t = Math.min((now - start) / duration, 1);
      var eased = 1 - Math.pow(1 - t, 3);
      el.textContent = formatCount(el, Math.round(target * eased));
      if (t < 1) { requestAnimationFrame(step); }
    };
    requestAnimationFrame(step);
  }

  /* ---------------------------------------------------- progress bars -----*/
  function initProgressBars(immediate) {
    var bars = document.querySelectorAll('.progress-bar[data-percent]');
    if (!bars.length) { return; }
    bars.forEach(function (bar) {
      var pct = bar.getAttribute('data-percent') + '%';
      if (immediate) { bar.style.setProperty('--pct', pct); return; }
      bar.style.setProperty('--pct', '0%');
      var po = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) { return; }
          po.unobserve(entry.target);
          requestAnimationFrame(function () { entry.target.style.setProperty('--pct', pct); });
        });
      }, { threshold: 0.4 });
      po.observe(bar);
    });
  }
  initProgressBars(false);

  /* --------------------------------------------- cursor-reactive cards ----*/
  /* A very small tilt — enough to feel alive, never enough to distract.
     Pointer-fine only, so it never fires on touch. */
  if (window.matchMedia('(pointer: fine)').matches) {
    document.querySelectorAll('[data-tilt]').forEach(function (card) {
      var frame = null;
      card.addEventListener('pointermove', function (e) {
        if (frame) { return; }
        frame = requestAnimationFrame(function () {
          frame = null;
          var r = card.getBoundingClientRect();
          var x = (e.clientX - r.left) / r.width - 0.5;
          var y = (e.clientY - r.top) / r.height - 0.5;
          card.style.transform =
            'perspective(900px) rotateX(' + (-y * 3).toFixed(2) + 'deg) rotateY(' +
            (x * 3).toFixed(2) + 'deg) translateY(-4px)';
        });
      });
      card.addEventListener('pointerleave', function () {
        card.style.transform = '';
      });
    });

    /* Magnetic primary CTA — the button leans toward the cursor as it approaches */
    document.querySelectorAll('[data-magnetic]').forEach(function (btn) {
      var frame = null;
      btn.addEventListener('pointermove', function (e) {
        if (frame) { return; }
        frame = requestAnimationFrame(function () {
          frame = null;
          var r = btn.getBoundingClientRect();
          var x = (e.clientX - r.left - r.width / 2) * 0.18;
          var y = (e.clientY - r.top - r.height / 2) * 0.24;
          btn.style.transform = 'translate(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px)';
        });
      });
      btn.addEventListener('pointerleave', function () { btn.style.transform = ''; });
    });
  }

  /* ------------------------------------------------ hero parallax drift ---*/
  var heroVisual = document.querySelector('[data-parallax]');
  if (heroVisual) {
    var ticking = false;
    window.addEventListener('scroll', function () {
      if (ticking) { return; }
      ticking = true;
      requestAnimationFrame(function () {
        ticking = false;
        var y = window.scrollY;
        if (y > 900) { return; }
        heroVisual.style.setProperty('--parallax', (y * -0.035).toFixed(2) + 'px');
      });
    }, { passive: true });
  }
})();
