/* ============================================================
   Motion — révélations, compteurs, vagues
   ============================================================ */
(function () {
  const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- Compteur animé : de 0 à la valeur réelle ----
     On anime depuis 0 plutôt que d'afficher une valeur qui « saute » :
     l'œil suit le chiffre, ce qui donne l'impression que la donnée arrive. */
  window.countUp = function (el) {
    const target = Number(el.dataset.count || 0);
    const suffix = el.dataset.suffix || '';
    if (RM || target === 0) {
      el.textContent = target.toLocaleString('fr-FR') + suffix;
      return;
    }
    const duration = 1100;
    const start = performance.now();
    const fmt = (v) => Math.round(v).toLocaleString('fr-FR') + suffix;
    function tick(now) {
      const t = Math.min(1, (now - start) / duration);
      // easeOutExpo : démarrage franc, arrivée douce.
      const eased = t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
      el.textContent = fmt(target * eased);
      if (t < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  };

  /* ---- Révélation à l'entrée dans le viewport, avec cascade ----
     `data-stagger` décale chaque enfant : l'ordre de lecture suit l'ordre
     visuel, sansanimation collective qui tasse tout au même instant. */
  window.observeReveal = function (root) {
    const targets = Array.from(root.querySelectorAll('[data-reveal]'));
    if (!targets.length) return;
    if (RM || !('IntersectionObserver' in window)) {
      targets.forEach((t) => t.classList.add('in'));
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const host = entry.target;
          const delay = Number(host.dataset.stagger || 0) * 60;
          const kids = host.querySelectorAll('[data-reveal-item]');
          if (kids.length) {
            kids.forEach((kid, i) => setTimeout(() => kid.classList.add('in'), i * 70 + delay));
          } else {
            setTimeout(() => host.classList.add('in'), delay);
          }
          io.unobserve(host);
        });
      },
      { threshold: 0.15 }
    );
    targets.forEach((t) => io.observe(t));
  };

  /* ---- Compteurs dès qu'ils entrent en vue ---- */
  window.observeCounters = function (root) {
    const counters = Array.from(root.querySelectorAll('[data-count]'));
    if (!counters.length) return;
    if (RM || !('IntersectionObserver' in window)) {
      counters.forEach(window.countUp);
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          window.countUp(entry.target);
          io.unobserve(entry.target);
        });
      },
      { threshold: 0.6 }
    );
    counters.forEach((c) => io.observe(c));
  };
})();