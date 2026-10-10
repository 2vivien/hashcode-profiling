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
    status.innerHTML = `
      <div class="card"><div class="k">Service</div><div class="v"><span class="dot ok"></span>opérationnel</div></div>
      <div class="card"><div class="k">Base de données</div><div class="v"><span class="dot ${dbCls}"></span>${dbTxt}</div></div>
      <div class="card"><div class="k">Modèle</div><div class="v sm">${esc(info.model_version)}</div></div>
      <div class="card"><div class="k">Connaissance</div><div class="v sm">${esc(info.knowledge_version)}</div></div>
      <div class="card"><div class="k">Uptime</div><div class="v">${Math.round(info.uptime_seconds)}s</div></div>
      <div class="card"><div class="k">Code</div><div class="v sm">${esc(info.code_version)}</div></div>`;
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
  } catch (e) {
    status.innerHTML = `<div class="card"><div class="k">Service</div><div class="v"><span class="dot ko"></span>injoignable</div></div>`;
    const box = status.closest('section') || status;
    const note = document.createElement('div');
    note.className = 'err-inline';
    note.style.marginTop = '16px';
    note.innerHTML = `<span class="ez" aria-hidden="true">!</span><div><b>Statut indisponible.</b><br>${esc(e.message)}</div>`;
    box.appendChild(note);
    Toast.error('Statut indisponible', e.message);
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
    info: () => Toast.info('Modèle mis à jour', 'deterministic-baseline-v1 est actif.'),
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
