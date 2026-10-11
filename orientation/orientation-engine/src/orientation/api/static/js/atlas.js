/* ============================================================
   Atlas — carte de couverture + répartitions
   Dépend des helpers globaux d'app.js : apiFetch, esc, pct.
   ============================================================ */

(function () {
  const root = document.getElementById('atlas');
  if (!root) return;

  /* La carte est un SVG déjà tracé côté serveur (Natural Earth) : on l'injecte
     tel quel. Les former 64 points sur une grille ne disait rien de la
     géographie — les vrais contours, si. */
  function mapMarkup(profession) {
    const url = '/v1/orientation/atlas/map.svg' + (profession ? '?profession=' + encodeURIComponent(profession) : '');
    return `<object class="atlas-svg" type="image/svg+xml" data="${url}" aria-label="Carte du monde des données">
      <p class="sub">Carte indisponible.</p>
    </object>`;
  }

  function barList(rows, unit) {
    if (!rows || !rows.length) return '<p class="sub">Aucune donnée.</p>';
    const max = Math.max(...rows.map((r) => r.count)) || 1;
    return `<div class="bars">${rows
      .map((r) => {
        const w = Math.max(2, Math.round((r.count / max) * 100));
        return `<div class="bar-row" data-reveal-item>
          <span class="bar-lbl" title="${esc(r.domain || r.country || r.gender || r.language)}">${esc(r.domain || r.country || r.gender || r.language)}</span>
          <span class="bar-track"><i style="--w:${w}%"></i></span>
          <span class="bar-val" data-count="${r.count}">${unit ? r.count.toLocaleString('fr-FR') + ' ' + unit : ''}</span>
        </div>`;
      })
      .join('')}</div>`;
  }

  async function render() {
    root.innerHTML = '<div class="card"><div class="sk sk-line w40"></div><div class="sk sk-line w70"></div></div>';
    let data;
    try {
      data = await apiFetch('/v1/orientation/atlas?limit=16');
    } catch (e) {
      root.innerHTML = `<div class="card"><div class="k">Atlas</div><div class="v sm">indisponible (${esc(e.message)})</div></div>`;
      return;
    }

    const cov = data.coverage || {};
    const totals = data.totals || {};
    const coveredList = (cov.country_names && Object.keys(cov.country_names).length)
      ? Object.entries(cov.country_names).map(([iso, name]) => `${name} (${iso})`).join(', ')
      : 'aucune';

    root.innerHTML = `
      <div class="atlas-grid">
        <div class="card atlas-map">
          <div class="k">Carte du monde</div>
          <div class="atlas-map-actions">
            <label class="atlas-q">Chercher un métier
              <input id="atlas-q" type="search" placeholder="géologue, ingénieur…" autocomplete="off">
            </label>
            <span class="atlas-hint">Contours réels · Natural Earth</span>
          </div>
          ${mapMarkup()}
          <p class="note">Un pays vert a des données réelles chargées. Les autres n'ont ni métier, ni compétence, ni marché du travail — nous préférons le montrer que le cacher.</p>
          <p class="note atlas-next">Le référentiel international de l'OIT (ISCO) n'est pas encore branché : chaque pays couvert repose sur sa propre nomenclature. C'est le prochain chantier.</p>
        </div>

        <div class="card">
          <div class="k">Volume</div>
          <div class="atlas-stats">
            <div><b data-count="${totals.occupations || 0}">0</b><span>métiers</span></div>
            <div><b data-count="${totals.competences || 0}">0</b><span>compétences</span></div>
            <div><b data-count="${totals.directions || 0}">0</b><span>directions</span></div>
            <div><b data-count="${totals.formations || 0}">0</b><span>formations</span></div>
          </div>
        </div>
      </div>

      <div class="atlas-grid" data-reveal>
        <div class="card"><div class="k">Métiers par grand domaine</div>${barList(data.occupations_by_domain)}</div>
        <div class="card"><div class="k">Compétences par domaine</div>${barList(data.competences_by_domain)}</div>
      </div>

      <div class="atlas-grid" data-reveal>
        <div class="card"><div class="k">Écriture inclusive des métiers</div>${barList(data.occupations_by_gender)}</div>
        <div class="card"><div class="k">Langues des données</div>${barList(data.occupations_by_language)}</div>
      </div>

      ${cov.note ? `<p class="note">${esc(cov.note)}</p>` : ''}
    `;

    /* Filtre par métier : recharge la carte côté serveur, qui sait faire le
       lien entre un métier et les fiches réelles de la connaissance. */
    const input = document.getElementById('atlas-q');
    const holder = root.querySelector('.atlas-map');
    if (input && holder) {
      let timer = null;
      input.addEventListener('input', () => {
        clearTimeout(timer);
        timer = setTimeout(() => {
          const query = input.value.trim();
          holder.querySelector('.atlas-svg')?.remove();
          holder.insertAdjacentHTML('afterbegin', mapMarkup(query).replace('atlas-svg', 'atlas-svg is-loading'));
        }, 350);
      });
    }

    const section = root.querySelector('#atlas');
    if (section) {
      window.observeReveal(section);
      window.observeCounters(section);
      const map = section.querySelector('.atlas-map');
      if (map) window.observeReveal(map);
    }
  }

  render();
})();