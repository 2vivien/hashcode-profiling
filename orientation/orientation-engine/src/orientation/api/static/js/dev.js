/* ============================================================
   Espace développeur — logique spécifique (/developers)
   Dépend des helpers globaux d'app.js : API, apiFetch, Toast, esc.
   ============================================================ */

/* ---- Statut système + table de connexion ---- */
(async function () {
  const status = document.getElementById('status');
  const conn = document.getElementById('conn');
  if (!status) return;

  status.innerHTML = `<div class="card">
    <div class="sk sk-line w40"></div><div class="sk sk-line w80"></div></div>
    <div class="card"><div class="sk sk-line w40"></div><div class="sk sk-line w60"></div></div>`;

  try {
    const info = await apiFetch('/v1/orientation/system/info');
    const db = info.database || {};
    const dbCls = db.reachable === true ? 'ok' : (db.reachable === false ? 'ko' : 'wait');
    const dbTxt = db.reachable === true ? 'Connectée' : (db.reachable === false ? 'Injoignable' : 'Non configurée');
    const counts = info.knowledge_counts || {};
    const occ = counts.occupations;
    const comp = counts.competences;
    status.innerHTML = `
      <div class="card"><div class="k">Service</div><div class="v"><span class="dot ok"></span>opérationnel</div></div>
      <div class="card"><div class="k">Base de données</div><div class="v"><span class="dot ${dbCls}"></span>${dbTxt}</div></div>
      <div class="card"><div class="k">Modèle</div><div class="v sm">${esc(info.model_version)}</div></div>
      <div class="card"><div class="k">Couches actives</div><div class="v">${(info.engine_layers || []).filter((l) => l.active).length} / ${(info.engine_layers || []).length}</div></div>
      <div class="card"><div class="k">Connaissance</div><div class="v sm">${esc(info.knowledge_version)}</div></div>
      <div class="card"><div class="k">Uptime</div><div class="v">${Math.round(info.uptime_seconds)}s</div></div>
      <div class="card"><div class="k">Code</div><div class="v sm">${esc(info.code_version)}</div></div>
      ${occ != null ? `<div class="card"><div class="k">Métiers</div><div class="v">${Number(occ).toLocaleString('fr-FR')}</div></div>` : ''}
      ${comp != null ? `<div class="card"><div class="k">Compétences</div><div class="v">${Number(comp).toLocaleString('fr-FR')}</div></div>` : ''}`;
    if (conn) {
      const rows = [
        ['Base URL', API],
        ['DB host', db.host || '—'],
        ['DB port', db.port || '—'],
        ['Knowledge disponible', (info.knowledge_versions_available || []).join(', ') || '—'],
        ['Profil / évaluation', `${info.profile_version} / ${info.assessment_version}`],
        ['Configuration', info.configuration_version],
        ['Chemin données', info.data_path],
      ];
      conn.innerHTML = `<div class="rows">${rows.map(([k, v]) =>
        `<div class="row"><span class="l">${esc(k)}</span><code>${esc(v)}</code></div>`).join('')}</div>`;
    }

    /* ---- Couches du moteur : état réel, pas une chaîne figée ---- */
    const layers = document.getElementById('layers');
    if (layers) {
      const items = info.engine_layers || [];
      if (!items.length) {
        layers.innerHTML = `<div class="card"><div class="k">Couches</div><div class="v sm">non rapportées</div></div>`;
      } else {
        layers.innerHTML = `<div class="rows">${items.map((l) => {
          const on = l.active === true;
          const label = on ? 'active' : 'inactive';
          return `<div class="row"><span class="l"><span class="dot ${on ? 'ok' : 'wait'}"></span> ${esc(l.layer)} · ${label}</span><code>${esc(l.reason || '')}</code></div>`;
        }).join('')}</div>`;
      }
    }

    /* ---- RAG ---- */
    const ragBox = document.getElementById('rag');
    if (ragBox) {
      const rag = info.rag || {};
      if (rag.indexed) {
        const kinds = rag.by_kind || {};
        const parts = Object.entries(kinds).map(([k, v]) => `${k} ${Number(v).toLocaleString('fr-FR')}`);
        ragBox.innerHTML = `<div class="rows">
          <div class="row"><span class="l"><span class="dot ok"></span> Index</span><code>${Number(rag.documents || 0).toLocaleString('fr-FR')} documents</code></div>
          <div class="row"><span class="l">Répartition</span><code>${esc(parts.join(' · ') || '—')}</code></div>
          <div class="row"><span class="l">Embeddings</span><code>${esc(rag.embedder || '—')} · ${rag.dimensions || 0} dims</code></div>
        </div>`;
      } else {
        ragBox.innerHTML = `<div class="card"><div class="k">Index RAG</div><div class="v sm">indisponible${rag.error ? ' (' + esc(rag.error) + ')' : ''}</div></div>`;
      }
    }
  } catch (e) {
    status.innerHTML = `<div class="card"><div class="k">Service</div><div class="v"><span class="dot ko"></span>injoignable</div></div>`;
    // Les couches et le RAG dépendent de la même réponse : sans elle, on ne
    // prétend rien du tout plutôt que d'afficher un état par défaut.
    for (const id of ['layers', 'rag']) {
      const box2 = document.getElementById(id);
      if (box2) box2.innerHTML = `<div class="card"><div class="k">—</div><div class="v sm">indisponible</div></div>`;
    }
    const box = status.closest('section') || status;
    const note = document.createElement('div');
    note.className = 'err-inline';
    note.style.marginTop = '16px';
    note.innerHTML = `<span class="ez" aria-hidden="true">!</span><div><b>Statut indisponible.</b><br>${esc(e.message)}</div>`;
    box.appendChild(note);
    Toast.error('Statut indisponible', e.message);
  }
})();

/* ---- Bandeau « état réel » de l'accueil : alimenté par l'API ---- */
(async function () {
  const grid = document.getElementById('status-grid');
  if (!grid) return;
  const note = document.getElementById('status-note');
  const cards = Array.prototype.slice.call(grid.querySelectorAll('.scard'));
  const setCard = (index, value, pill, ok) => {
    const card = cards[index];
    if (!card) return;
    const val = card.querySelector('.val');
    const badge = card.querySelector('.pill');
    if (val) val.textContent = value;
    if (badge) {
      badge.textContent = pill;
      badge.classList.toggle('ok', ok);
      badge.classList.toggle('wait', !ok);
    }
  };

  try {
    const info = await apiFetch('/v1/orientation/system/info');
    const counts = info.knowledge_counts || {};
    const rag = info.rag || {};
    const layers = info.engine_layers || [];
    const learned = layers.filter((l) => l.active && l.layer !== 'fairness');

    setCard(1, `${Number(counts.occupations || 0).toLocaleString('fr-FR')} métiers`, counts.occupations ? 'ROME v3' : 'Curé', true);
    setCard(2, rag.indexed ? `${Number(rag.documents || 0).toLocaleString('fr-FR')} docs` : 'Indisponible', rag.indexed ? 'Index actif' : 'Non indexé', rag.indexed === true);
    setCard(3, `${learned.length} / ${layers.length} actives`, learned.length ? 'Modèle en service' : 'Score déterministe seul', learned.length > 0);

    // On n'affiche une note que s'il reste quelque chose d'honnête à signaler.
    const inactive = layers.filter((l) => !l.active && l.layer !== 'fairness');
    if (note && inactive.length) {
      note.hidden = false;
      note.textContent = `Les couches apprises (calibration, ranking, graphe, bandit) sont branchées mais inactives : aucun modèle entraîné. Le score affiché est intégralement déterministe et reproductible.`;
    }
  } catch {
    setCard(1, 'Indisponible', 'État non lu', false);
    setCard(2, 'Indisponible', 'État non lu', false);
    setCard(3, 'Indisponible', 'État non lu', false);
  }
})();

/* ---- Snippets copiables ---- */
(function () {
  const pre = document.getElementById('snippet');
  const tabs = document.getElementById('tabs');
  if (!pre || !tabs) return;
  const host = location.host;
  const S = {
    curl:
`# État du service
curl -s https://${host}/v1/orientation/system/info

# Directions pour un profil
curl -s -X POST https://${host}/v1/orientation/recommendations \\
  -H "Content-Type: application/json" \\
  -d '{"student_id":"dev-1","interests":{"investigative":0.8},
       "abilities":{"logical":0.9},
       "skills":[{"skill_id":"programming","level":0.8,
                  "confidence":0.7,"source":"declared","status":"declared"}]}'`,
    node:
`// Node / TypeScript
const BASE = "https://${host}";
const res = await fetch(\`\${BASE}/v1/orientation/recommendations\`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    student_id: "dev-1",
    interests: { investigative: 0.8 },
    abilities: { logical: 0.9 },
    skills: [{ skill_id: "programming", level: 0.8,
               confidence: 0.7, source: "declared", status: "declared" }]
  })
});
if (!res.ok) throw new Error(\`HTTP \${res.status}\`);
const { candidates } = await res.json();
console.log(candidates.map(c => c.direction_name));`,
    python:
`# Python
import requests
BASE = "https://${host}"
profile = {
  "student_id": "dev-1",
  "interests": {"investigative": 0.8},
  "abilities": {"logical": 0.9},
  "skills": [{"skill_id": "programming", "level": 0.8,
              "confidence": 0.7, "source": "declared", "status": "declared"}],
}
r = requests.post(f"{BASE}/v1/orientation/recommendations", json=profile, timeout=10)
r.raise_for_status()
for c in r.json()["candidates"]:
    print(c["direction_name"], round(c["score"], 3))`,
    psql:
`# Supabase Postgres (self-hosted, réseau interne)
# Mot de passe dans .env — jamais exposé ici.
psql "postgresql://postgres@${host}:5432/postgres"

# Depuis le réseau hashcodeprofiling-net :
psql "postgresql://postgres:****@hashcodeprofiling-db:5432/postgres"`
  };
  const colorize = (code) => esc(code)
    .replace(/(#[^\n]*)/g, '<span class="tok-cm">$1</span>')
    .replace(/(".*?")/g, '<span class="tok-str">$1</span>')
    .replace(/\b(curl|const|await|import|requests|psql|for|in|print|def|return)\b/g, '<span class="tok-cmd">$1</span>')
    .replace(/(--?[a-zA-Z-]+)/g, '<span class="tok-flag">$1</span>');
  const set = (key) => { pre.innerHTML = colorize(S[key]); };
  tabs.addEventListener('click', e => {
    const b = e.target.closest('.tab'); if (!b) return;
    tabs.querySelectorAll('.tab').forEach(t => t.classList.toggle('on', t === b));
    set(b.dataset.t);
  });
  set('curl');
  const copy = document.querySelector('[data-copy]');
  if (copy) copy.onclick = async (e) => {
    const b = e.currentTarget;
    try {
      await navigator.clipboard.writeText(pre.textContent);
      const old = b.textContent; b.textContent = 'Copié ✓';
      setTimeout(() => b.textContent = old, 1400);
      Toast.success('Copié dans le presse-papiers');
    } catch {
      Toast.warn('Copie impossible', 'Sélectionnez le texte manuellement.');
    }
  };
})();

/* ---- Bac à sable des toasts ---- */
(function () {
  const btns = document.querySelectorAll('[data-toast]');
  if (!btns.length) return;
  const samples = {
    success: () => Toast.success('Direction enregistrée', '3 pistes ajoutées au profil.'),
    info: async () => {
      // Le nom du modèle venait de l'API : une chaîne figée serait fausse dès le
      // premier modèle entraîné.
      try {
        const info = await apiFetch('/v1/orientation/system/info');
        const active = (info.engine_layers || []).filter((l) => l.active).map((l) => l.layer);
        const detail = active.length
          ? `${info.model_version} · couches actives : ${active.join(', ')}`
          : `${info.model_version} · score déterministe seul`;
        Toast.info('Modèle en service', detail);
      } catch {
        Toast.info('Modèle en service', 'État indisponible.');
      }
    },
    warn: () => Toast.warn('Données partielles', 'Certaines dimensions restent incertaines.'),
    error: () => Toast.error('Requête échouée', 'HTTP 422 — champ "student_id" manquant.'),
    action: () => Toast.warn('Direction retirée', 'Le profil a été mis à jour.', {
      action: { label: 'Annuler', onClick: () => Toast.success('Action annulée', 'La direction a été restaurée.') },
    }),
  };
  btns.forEach(b => b.addEventListener('click', () => (samples[b.dataset.toast] || samples.info)()));
})();
(function () {
  const out = document.getElementById('out'), btn = document.getElementById('send-dev'), ta = document.getElementById('payload');
  if (!out || !btn || !ta) return;
  btn.onclick = async () => {
    btn.disabled = true; out.hidden = false;
    out.innerHTML = '<span class="sk sk-line w60"></span><span class="sk sk-line w80"></span><span class="sk sk-line w40"></span>';
    try {
      let body;
      try { body = JSON.parse(ta.value); }
      catch (e) { throw new Error('JSON invalide : ' + e.message); }
      const data = await apiFetch('/v1/orientation/recommendations', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
      });
      out.textContent = JSON.stringify(data, null, 2);
      Toast.success('Réponse 200', `${(data.candidates || []).length} piste(s) retournée(s).`);
    } catch (e) {
      out.innerHTML = `<div class="err-inline"><span class="ez" aria-hidden="true">!</span><div><b>${e.status ? 'HTTP ' + e.status : 'Erreur'}.</b> ${esc(e.message)}</div></div>`;
      Toast.error(e.status ? `Erreur ${e.status}` : 'Erreur', e.message);
    } finally { btn.disabled = false; }
  };
})();
