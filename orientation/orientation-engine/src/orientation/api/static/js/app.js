/* ============================================================
   hashcode.profiling — JavaScript partagé (motion + démo)
   Chargé par base.html sur toutes les pages. Tout est optionnel :
   chaque bloc vérifie la présence de ses éléments.
   ============================================================ */
const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
const API = location.origin;
const $ = (s, r) => (r && typeof r.querySelector === 'function' ? r : document).querySelector(s);
const $$ = (s, r) => [...((r && typeof r.querySelectorAll === 'function' ? r : document).querySelectorAll(s))];
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

/* ---- Toasts : notifications accessibles et dismissibles ---- */
const Toast = (() => {
  const wrap = () => $('#toasts');
  const ICON = { success: '✓', error: '✕', warn: '!', info: 'i' };
  const TITLE = { success: 'Succès', error: 'Erreur', warn: 'Attention', info: 'Information' };
  function show(type, title, msg, opts = {}) {
    const host = wrap();
    if (!host) return { dismiss() {} };
    const timeout = opts.timeout ?? (opts.action ? 8000 : (type === 'error' ? 7000 : 4500));
    const el = document.createElement('div');
    el.className = 'toast ' + type;
    el.setAttribute('role', type === 'error' ? 'alert' : 'status');
    el.innerHTML =
      `<i class="ic" aria-hidden="true">${ICON[type] || 'i'}</i>` +
      `<div class="bodyx"><div class="tt">${esc(title ?? TITLE[type])}</div>${msg ? `<div class="ms">${esc(msg)}</div>` : ''}</div>` +
      (opts.action ? `<button class="act">${esc(opts.action.label)}</button>` : '') +
      `<button class="close" aria-label="Fermer la notification">×</button>` +
      (timeout > 0 ? '<span class="bar"></span>' : '');
    const bar = el.querySelector('.bar');
    if (bar) bar.style.animationDuration = timeout + 'ms';
    let timer = null;
    const dismiss = () => {
      if (timer) clearTimeout(timer);
      el.classList.add('leaving');
      el.addEventListener('animationend', () => el.remove(), { once: true });
      setTimeout(() => el.remove(), 450);
    };
    el.querySelector('.close').onclick = dismiss;
    const act = el.querySelector('.act');
    if (act) act.onclick = () => { opts.action.onClick?.(); dismiss(); };
    if (timeout > 0) {
      el.addEventListener('pointerenter', () => { clearTimeout(timer); if (bar) bar.style.animationPlayState = 'paused'; });
      el.addEventListener('pointerleave', () => { if (bar) bar.style.animationPlayState = 'running'; timer = setTimeout(dismiss, timeout); });
      timer = setTimeout(dismiss, timeout);
    }
    host.appendChild(el);
    return { dismiss };
  }
  addEventListener('keydown', (e) => { if (e.key === 'Escape') $$('.toast', $('#toasts') || document).forEach(t => t.querySelector('.close')?.click()); });
  return {
    show,
    success: (t, m, o) => show('success', t, m, o),
    error: (t, m, o) => show('error', t, m, o),
    warn: (t, m, o) => show('warn', t, m, o),
    info: (t, m, o) => show('info', t, m, o),
  };
})();

/* ---- Erreurs lisibles à partir d'une réponse API ---- */
function humanError(status, data) {
  if (status === 422 && data && Array.isArray(data.detail)) {
    return data.detail.map(d => `${(d.loc || []).slice(1).join('.') || 'champ'} : ${d.msg}`).join(' · ');
  }
  if (data && typeof data.detail === 'string') return data.detail;
  if (status === 404) return 'Ressource introuvable (404).';
  if (status === 429) return 'Trop de requêtes — patientez un instant.';
  if (status >= 500) return `Erreur serveur (${status}). Réessayez.`;
  return `Erreur HTTP ${status}.`;
}

/* ---- Fetch unifié : parse + erreurs structurées ---- */
async function apiFetch(path, options = {}) {
  let res;
  try {
    res = await fetch(API + path, options);
  } catch (e) {
    const err = new Error('Service injoignable. Vérifiez votre connexion ou réessayez.');
    err.status = 0; err.cause = e; throw err;
  }
  const ct = res.headers.get('content-type') || '';
  const data = ct.includes('application/json') ? await res.json().catch(() => null) : null;
  if (!res.ok) {
    const err = new Error(humanError(res.status, data));
    err.status = res.status; err.data = data; throw err;
  }
  return data;
}

/* ---- Filet de sécurité global ---- */
addEventListener('unhandledrejection', (e) => { Toast.error('Erreur inattendue', e.reason?.message || 'Une opération a échoué.'); });
addEventListener('error', (e) => { if (e.message) Toast.error('Erreur', e.message); });

/* ---- Modale accessible (<dialog>) ---- */
const Modal = (() => {
  const dlg = () => $('#modal');
  function open({ title, body, actions = [] }) {
    const d = dlg();
    if (!d) return;
    d.innerHTML =
      `<div class="mhead"><h3 id="modalTitle">${esc(title || '')}</h3>` +
      `<button class="x" aria-label="Fermer">×</button></div>` +
      `<div class="mbody">${body || ''}</div>` +
      (actions.length ? `<div class="mfoot">${actions.map((a, i) =>
        `<button class="btn ${a.variant || 'ghost'}" data-mi="${i}">${esc(a.label)}</button>`).join('')}</div>` : '');
    d.querySelector('.x').onclick = () => d.close();
    d.querySelectorAll('[data-mi]').forEach(b => b.onclick = () => { actions[+b.dataset.mi]?.onClick?.(); d.close(); });
    d.onclick = (e) => { if (e.target === d) d.close(); };
    if (!d.open) d.showModal();
  }
  return { open, close: () => dlg()?.close() };
})();

/* ---- Menu mobile accessible ---- */
(function () {
  const toggle = $('#navToggle'), menu = $('#navMenu');
  if (!toggle || !menu) return;
  const setOpen = (open) => {
    menu.classList.toggle('open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.textContent = open ? '✕' : '☰';
  };
  toggle.onclick = () => setOpen(!menu.classList.contains('open'));
  menu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => setOpen(false)));
  addEventListener('keydown', (e) => { if (e.key === 'Escape') setOpen(false); });
  addEventListener('click', (e) => { if (!menu.contains(e.target) && e.target !== toggle) setOpen(false); });
})();

/* ---- Nav : état scroll + progression + retour en haut ---- */
(function () {
  const nav = $('#nav'), prog = $('#progress'), totop = $('#totop');
  if (!nav) return;
  const onScroll = () => {
    const y = scrollY;
    nav.classList.toggle('scrolled', y > 30);
    if (prog) {
      const h = document.documentElement.scrollHeight - innerHeight;
      prog.style.width = (h > 0 ? (y / h) * 100 : 0) + '%';
    }
    if (totop) totop.classList.toggle('show', y > innerHeight * .8);
  };
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  if (totop) totop.onclick = () => scrollTo({ top: 0, behavior: RM ? 'auto' : 'smooth' });
})();

/* ---- Révélation au scroll (native scroll-driven si dispo) ---- */
(function () {
  const els = $$('.reveal');
  if (!els.length) return;
  if (!RM && typeof CSS !== 'undefined' && CSS.supports && CSS.supports('animation-timeline: view()')) {
    document.documentElement.classList.add('sdr');
    return;
  }
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e, i) => {
      if (e.isIntersecting) {
        setTimeout(() => e.target.classList.add('in'), RM ? 0 : i * 70);
        io.unobserve(e.target);
      }
    });
  }, { threshold: .12 });
  els.forEach(el => io.observe(el));
})();

/* ---- Titre mot-à-mot ---- */
(function () {
  const h1 = $('h1');
  if (!h1) return;
  const walk = (node) => {
    [...node.childNodes].forEach(child => {
      if (child.nodeType === 3) {
        const frag = document.createDocumentFragment();
        child.textContent.split(/(\s+)/).forEach(tok => {
          if (/^\s+$/.test(tok) || tok === '') { frag.appendChild(document.createTextNode(tok)); return; }
          const s = document.createElement('span'); s.className = 'word'; s.textContent = tok; frag.appendChild(s);
        });
        child.replaceWith(frag);
      } else if (child.nodeType === 1) {
        if (child.classList.contains('g') || child.tagName === 'A') { child.classList.add('word'); }
        else walk(child);
      }
    });
  };
  walk(h1);
  $$('.word', h1).forEach((w, i) => setTimeout(() => w.classList.add('in'), RM ? 0 : 120 + i * 90));
})();

/* ---- Parallaxe (blobs + pipe) ---- */
(function () {
  if (RM) return;
  let sy = 0, ticking = false;
  const b = ['.b1', '.b2', '.b3'].map($);
  const pipe = $('#pipe');
  if (!b.some(Boolean) && !pipe) return;
  const frame = () => {
    if (b[0]) b[0].style.transform = `translateY(${sy * 0.08}px)`;
    if (b[1]) b[1].style.transform = `translateY(${sy * -0.05}px)`;
    if (b[2]) b[2].style.transform = `translateY(${sy * 0.06}px)`;
    if (pipe && sy < innerHeight) pipe.style.transform = `perspective(1000px) rotateY(-4deg) translateY(${sy * -0.03}px)`;
    ticking = false;
  };
  addEventListener('scroll', () => { sy = scrollY; if (!ticking) { ticking = true; requestAnimationFrame(frame); } }, { passive: true });
  frame();
})();

/* ---- Pipeline interactif + cycle ---- */
(function () {
  const stages = $$('#pipe .stage');
  if (!stages.length) return;
  const desc = $('#pipeDesc');
  let idx = 0, paused = false;
  const show = (el) => {
    stages.forEach(s => s.classList.remove('on', 'active'));
    el.classList.add('on', 'active');
    if (desc && el.dataset.desc) desc.innerHTML = el.dataset.desc;
  };
  show(stages[0]); idx = 1;
  if (!RM) setInterval(() => {
    if (paused) return;
    show(stages[idx % stages.length]); idx++;
  }, 1100);
  stages.forEach(el => {
    el.addEventListener('pointerenter', () => { paused = true; show(el); });
    el.addEventListener('focus', () => { paused = true; show(el); });
    el.addEventListener('click', () => show(el));
  });
  const pipe = $('#pipe');
  if (pipe) pipe.addEventListener('pointerleave', () => { paused = false; });
})();

/* ---- Spotlight au curseur ---- */
(function () {
  if (RM) return;
  const spot = $('#spot');
  if (!spot) return;
  let shown = false;
  addEventListener('pointermove', (e) => {
    spot.style.setProperty('--mx', e.clientX + 'px');
    spot.style.setProperty('--my', e.clientY + 'px');
    if (!shown) { spot.style.opacity = '1'; shown = true; }
  }, { passive: true });
})();

/* ---- Tilt 3D + glow ---- */
(function () {
  if (RM) return;
  $$('.step, .scard, .panel').forEach(card => {
    const inner = document.createElement('div');
    inner.className = 'tilt-in';
    while (card.firstChild) inner.appendChild(card.firstChild);
    card.appendChild(inner);
    card.addEventListener('pointermove', (e) => {
      const r = card.getBoundingClientRect();
      const px = (e.clientX - r.left) / r.width, py = (e.clientY - r.top) / r.height;
      inner.style.transform = `perspective(900px) rotateX(${(0.5 - py) * 9}deg) rotateY(${(px - 0.5) * 11}deg)`;
      card.style.background = `radial-gradient(460px circle at ${e.clientX - r.left}px ${e.clientY - r.top}px, rgba(99,102,241,.14), var(--card) 62%)`;
    }, { passive: true });
    card.addEventListener('pointerleave', () => { inner.style.transform = ''; card.style.background = ''; });
  });
})();

/* ---- Boutons magnétiques ---- */
(function () {
  if (RM) return;
  $$('.btn, .nav-cta').forEach(btn => {
    btn.classList.add('mag');
    btn.addEventListener('pointermove', (e) => {
      const r = btn.getBoundingClientRect();
      btn.style.transform = `translate(${(e.clientX - (r.left + r.width / 2)) * 0.18}px, ${(e.clientY - (r.top + r.height / 2)) * 0.28}px)`;
    }, { passive: true });
    btn.addEventListener('pointerleave', () => { btn.style.transform = ''; });
  });
})();

/* ---- Coloration syntaxique JSON (éditeur) ---- */
function hlJSON(str) {
  const esc = str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  return esc.replace(/("(?:\\.|[^"\\])*")(\s*:)?|\b(true|false|null)\b|(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)|([{}\[\],:])/g,
    (m, s, colon, bool, num, punc) => {
      if (s !== undefined) return colon ? `<span class="tok-key">${s}</span><span class="tok-punc">${colon}</span>` : `<span class="tok-str">${s}</span>`;
      if (bool !== undefined) return `<span class="tok-bool">${bool}</span>`;
      if (num !== undefined) return `<span class="tok-num">${num}</span>`;
      if (punc !== undefined) return `<span class="tok-punc">${punc}</span>`;
      return m;
    });
}
(function () {
  const ta = $('#payload'), hl = $('#hl'), pre = $('.editor pre.hl');
  if (!ta || !hl || !pre) return;
  const status = $('#jsonStatus');
  const render = () => { hl.innerHTML = hlJSON(ta.value) + '\n'; };
  const validate = () => {
    if (!status) return;
    try {
      JSON.parse(ta.value);
      status.className = 'field-status ok';
      status.textContent = '· JSON valide';
      ta.removeAttribute('aria-invalid');
    } catch (e) {
      status.className = 'field-status ko';
      status.textContent = '· JSON invalide';
      ta.setAttribute('aria-invalid', 'true');
    }
  };
  ta.addEventListener('input', () => { render(); validate(); });
  ta.addEventListener('scroll', () => { pre.scrollTop = ta.scrollTop; pre.scrollLeft = ta.scrollLeft; }, { passive: true });
  render(); validate();
})();

/* ---- Démo live (accueil) ---- */
(function () {
  const results = $('#results'), btn = $('#send'), ta = $('#payload');
  if (!results || !btn || !ta) return;
  const statusEl = $('#apiStatus'), metaEl = $('#apiMeta');
  let lastBody = null;

  const pct = v => Math.round(v * 100);
  const setStatus = (text, cls) => { if (statusEl) { statusEl.textContent = text; statusEl.className = 'status ' + (cls || ''); } };

  const card = (item) => {
    const gaps = (item.skill_gaps || []).slice(0, 6)
      .map(g => `<span class="chip">${esc(g.skill_id)} · écart ${pct(g.gap)}%</span>`).join('');
    const el = document.createElement('article');
    el.className = 'rcard';
    el.innerHTML = `
      <div class="rc-head">
        <div><h3>${esc(item.direction_name)}</h3><span class="tax">${esc(item.taxonomy)}</span></div>
        <div class="score-ring" data-p="${pct(item.score)}"><span>${pct(item.score)}<small>%</small></span></div>
      </div>
      <div class="rc-metrics">
        <div class="mini"><span>Confiance</span><div class="bar conf"><i data-w="${pct(item.confidence)}"></i></div><b>${pct(item.confidence)}%</b></div>
        <div class="mini"><span>Incertitude</span><div class="bar unc"><i data-w="${pct(item.uncertainty)}"></i></div><b>${pct(item.uncertainty)}%</b></div>
      </div>
      ${gaps ? `<div class="gaps">${gaps}</div>` : ''}
      <div class="rc-foot"><span>Compatibilité expliquée</span><span>Voir le détail →</span></div>`;
    el.style.cursor = 'pointer';
    el.title = 'Voir le détail du score';
    el.onclick = () => {
      const b = item.score_breakdown || {};
      const rows = Object.entries(b).map(([k, v]) =>
        `<div class="metric"><div class="mh"><span>${esc(k)}</span><span>${Math.round(v * 100)}%</span></div>` +
        `<div class="bar"><i data-w="${Math.round(v * 100)}"></i></div></div>`).join('');
      const facts = (item.explanation?.facts || []).slice(0, 6)
        .map(f => `<div class="fact">${esc(f.dimension)} · ${esc(f.statement_key)}${f.value != null ? ' — ' + Math.round(f.value * 100) + '%' : ''}</div>`).join('');
      Modal.open({
        title: item.direction_name,
        body:
          `<p class="sub" style="margin:0 0 14px">Compatibilité ${Math.round(item.score * 100)}% · confiance ${Math.round(item.confidence * 100)}% · incertitude ${Math.round(item.uncertainty * 100)}%</p>` +
          `<h4 style="font-size:.8rem;text-transform:uppercase;letter-spacing:.12em;color:var(--muted);margin-bottom:10px">Décomposition du score</h4>` +
          `<div class="breakdown">${rows}</div>` +
          (facts ? `<h4 style="font-size:.8rem;text-transform:uppercase;letter-spacing:.12em;color:var(--muted);margin:18px 0 4px">Éléments retenus</h4><div class="facts">${facts}</div>` : ''),
        actions: [{ label: 'Fermer', variant: 'ghost' }],
      });
      requestAnimationFrame(() => setTimeout(() =>
        $$('#modal .bar>i[data-w]').forEach(x => x.style.width = x.dataset.w + '%'), 60));
    };
    return el;
  };

  const skeleton = () => {
    results.innerHTML = Array.from({ length: 2 }).map(() => `
      <div class="rcard" style="animation:none;opacity:1;transform:none">
        <div class="sk sk-line w60"></div>
        <div class="sk sk-line w80"></div>
        <div class="sk sk-line w80"></div>
        <div class="sk sk-line w40"></div>
      </div>`).join('');
  };

  const render = (data) => {
    results.innerHTML = '';
    (data.candidates || []).forEach((it, i) => {
      const c = card(it); c.style.animationDelay = (i * 90) + 'ms'; results.appendChild(c);
    });
    if (!data.candidates?.length) results.innerHTML = '<div class="empty">Aucune direction retenue pour ce profil.</div>';
    requestAnimationFrame(() => setTimeout(() => {
      $$('.bar>i[data-w]', results).forEach(b => b.style.width = b.dataset.w + '%');
      $$('.score-ring', results).forEach(r => r.style.setProperty('--p', r.dataset.p));
    }, 60));
  };

  const showError = (message) => {
    setStatus('erreur', 'err');
    if (metaEl) metaEl.textContent = '';
    results.innerHTML =
      `<div class="err-inline"><span class="ez" aria-hidden="true">!</span>` +
      `<div><b>Échec de la requête.</b><br>${esc(message)}<br>` +
      `<button class="btn ghost" id="retry" style="margin-top:12px;padding:8px 16px;font-size:.82rem">Réessayer</button></div></div>`;
    $('#retry')?.addEventListener('click', () => run(lastBody));
    Toast.error('Requête échouée', message);
  };

  const run = async (body) => {
    if (!body) return;
    btn.disabled = true;
    setStatus('en cours…', '');
    skeleton();
    try {
      const data = await apiFetch('/v1/orientation/recommendations', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
      });
      render(data);
      setStatus(`200 ${data.candidates?.length ?? 0}×`, 'ok');
      if (metaEl) metaEl.textContent = `${data.model_version} · knowledge ${data.knowledge_version}`;
      Toast.success('Directions générées', `${(data.candidates || []).length} piste(s) · modèle ${data.model_version}`);
    } catch (e) {
      showError(e.message);
    } finally {
      btn.disabled = false;
    }
  };

  btn.onclick = () => {
    let body;
    try { body = JSON.parse(ta.value); }
    catch (e) {
      results.innerHTML = '';
      showError('JSON invalide : ' + e.message);
      return;
    }
    lastBody = body;
    run(body);
  };

  const copy = $('#apiCopy');
  if (copy) copy.onclick = async () => {
    try {
      await navigator.clipboard.writeText(API + '/v1/orientation/recommendations');
      Toast.success('URL copiée');
    } catch { Toast.warn('Copie impossible'); }
  };

  if (!RM) setTimeout(() => btn.click(), 900);
})();
