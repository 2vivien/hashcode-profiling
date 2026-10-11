/* ============================================================
   Atlas — carte de couverture + répartitions
   Dépend des helpers globaux d'app.js : apiFetch, esc, pct.
   ============================================================ */

(function () {
  const root = document.getElementById('atlas');
  if (!root) return;

  /* Projection équirectangulaire : x ∈ [0,1] ↔ longitude [-180,180],
     y ∈ [0,1] ↔ latitude [83,-56]. Simple, sans dépendance, et exacte
     pour placer des points — on ne cherche pas à dessiner des frontières. */
  function project(lat, lon) {
    return { x: (lon + 180) / 360, y: (83 - lat) / 139 };
  }

  /* Positions des nationsAfrican +iphers, pour la carte de couverture.
     Latitude/longitude ≈ capitale ou centroïde. */
  const COUNTRIES = [
    ['FR', 'France', 46.2, 2.2, 'covered'],
    ['BE', 'Belgique', 50.5, 4.5, ''],
    ['LU', 'Luxembourg', 49.8, 6.1, ''],
    ['CH', 'Suisse', 46.8, 8.2, ''],
    ['MA', 'Maroc', 31.8, -7.1, ''],
    ['DZ', 'Algérie', 28.0, 2.6, ''],
    ['TN', 'Tunisie', 33.9, 9.5, ''],
    ['EG', 'Égypte', 26.8, 30.8, ''],
    ['SN', 'Sénégal', 14.5, -14.5, ''],
    ['GM', 'Gambie', 13.4, -15.3, ''],
    ['GN', 'Guinée', 9.9, -9.7, ''],
    ['GW', 'Guinée-Bissau', 11.9, -15.6, ''],
    ['SL', 'Sierra Leone', 8.5, -11.8, ''],
    ['LR', 'Liberia', 6.4, -10.8, ''],
    ['CI', "Côte d'Ivoire", 7.5, -5.5, ''],
    ['GH', 'Ghana', 7.9, -1.0, ''],
    ['TG', 'Togo', 8.6, 0.8, ''],
    ['BJ', 'Bénin', 9.3, 2.3, ''],
    ['BF', 'Burkina Faso', 12.2, -1.6, ''],
    ['ML', 'Mali', 17.6, -4.0, ''],
    ['NE', 'Niger', 13.5, 2.1, ''],
    ['TD', 'Tchad', 15.5, 18.7, ''],
    ['SD', 'Soudan', 15.6, 30.2, ''],
    ['SS', 'Soudan du Sud', 6.9, 31.3, ''],
    ['ET', 'Éthiopie', 9.1, 40.5, ''],
    ['ER', 'Érythrée', 15.2, 39.8, ''],
    ['DJ', 'Djibouti', 11.8, 42.6, ''],
    ['SO', 'Somalie', 5.2, 46.2, ''],
    ['KE', 'Kenya', -0.0, 37.9, ''],
    ['UG', 'Ouganda', 1.4, 32.3, ''],
    ['RW', 'Rwanda', -1.9, 29.9, ''],
    ['BI', 'Burundi', -3.4, 29.9, ''],
    ['TZ', 'Tanzanie', -6.4, 34.9, ''],
    ['MW', 'Malawi', -13.3, 34.3, ''],
    ['ZM', 'Zambie', -13.1, 27.8, ''],
    ['ZW', 'Zimbabwe', -19.0, 29.2, ''],
    ['MZ', 'Mozambique', -18.7, 35.5, ''],
    ['AO', 'Angola', -11.2, 17.9, ''],
    ['CD', 'RD Congo', -4.0, 21.8, ''],
    ['CG', 'Congo', -0.2, 15.8, ''],
    ['GA', 'Gabon', -0.7, 11.8, ''],
    ['CM', 'Cameroun', 5.9, 12.4, ''],
    ['CF', 'République centrafricaine', 6.6, 20.9, ''],
    ['TD2', 'Tchad (nord)', 15.5, 18.7, ''],
    ['NG', 'Nigeria', 9.1, 8.7, ''],
    ['GH2', 'Ghana (est)', 7.9, -1.0, ''],
    ['CMR', 'Cameroun (nord)', 6.5, 12.5, ''],
    ['NA', 'Namibie', -22.6, 17.1, ''],
    ['BW', 'Botswana', -22.3, 24.7, ''],
    ['ZA', 'Afrique du Sud', -30.6, 22.9, ''],
    ['LS', 'Lesotho', -29.6, 28.2, ''],
    ['SZ', 'Eswatini', -26.5, 31.5, ''],
    ['MG', 'Madagascar', -18.8, 46.3, ''],
    ['MU', 'Maurice', -20.3, 57.6, ''],
    ['KM', 'Comores', -11.7, 43.3, ''],
    ['US', 'États-Unis', 39.8, -98.6, ''],
    ['CA', 'Canada', 56.1, -106.3, ''],
    ['BR', 'Brésil', -14.2, -51.9, ''],
    ['IN', 'Inde', 20.6, 79.0, ''],
    ['CN', 'Chine', 35.9, 104.2, ''],
    ['ES', 'Espagne', 40.5, -3.7, ''],
    ['DE', 'Allemagne', 51.2, 10.4, ''],
    ['IT', 'Italie', 41.9, 12.6, ''],
    ['GB', 'Royaume-Uni', 55.4, -3.4, ''],
  ];

  function buildMap(countries, countsByIso) {
    const seen = new Set();
    const parts = [];
    for (const [iso, name, lat, lon, flag] of countries) {
      if (seen.has(iso)) continue;
      seen.add(iso);
      const p = project(lat, lon);
      const count = countsByIso[iso] || 0;
      const covered = count > 0;
      const r = covered ? 6 : 2.6;
      const fill = covered ? 'var(--ok, #2ecc71)' : 'rgba(150,160,175,.35)';
      const title = covered
        ? `${name} — ${count.toLocaleString('fr-FR')} métiers`
        : `${name} — non couvert`;
      // La vague monte du sud vers le nord : la carte « se dessine » au lieu
      // d'apparaître d'un bloc, et l'œil suit un ordre géographique.
      const delay = (p.y * 900).toFixed(0);
      if (covered) {
        // Onde : un cercle qui s'ouvre et s'efface, en boucle, pour signaler
        // visuellement le seul pays réellement couvert.
        parts.push(
          `<circle cx="${(p.x * 100).toFixed(2)}" cy="${(p.y * 100).toFixed(2)}" r="6" class="map-ripple" style="animation-delay:${delay}ms"/>`
        );
      }
      parts.push(
        `<circle cx="${(p.x * 100).toFixed(2)}" cy="${(p.y * 100).toFixed(2)}" r="${r}" fill="${fill}" class="dot-map${covered ? ' covered' : ''}" style="animation-delay:${delay}ms"><title>${esc(title)}</title></circle>`
      );
      if (covered) {
        parts.push(
          `<text x="${(p.x * 100).toFixed(2)}" y="${(p.y * 100 - 1.6).toFixed(2)}" class="lbl-map" style="animation-delay:${(Number(delay) + 700).toFixed(0)}ms">${esc(iso)}</text>`
        );
      }
    }
    return parts.join('');
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
    const countsByIso = {};
    for (const row of data.occupations_by_country || []) countsByIso[row.country] = row.count;

    const coveredList = (cov.country_names && Object.keys(cov.country_names).length)
      ? Object.entries(cov.country_names).map(([iso, name]) => `${name} (${iso})`).join(', ')
      : 'aucune';

    root.innerHTML = `
      <div class="atlas-grid">
        <div class="card atlas-map">
          <div class="k">Couverture géographique</div>
          <svg viewBox="0 0 100 100" preserveAspectRatio="none" role="img" aria-label="Carte de couverture des données par pays">
            <rect x="0" y="0" width="100" height="100" class="map-bg"></rect>
            ${buildMap(COUNTRIES, countsByIso)}
          </svg>
          <p class="sub atlas-note">
            Couvert : <b>${esc(coveredList)}</b><br>
            Autorité : ${esc(cov.authority || '—')} · ${esc(cov.license || '—')}
            ${cov.retrieved_at ? ' · données de ' + esc(cov.retrieved_at) : ''}
          </p>
          <p class="note">Un point plein = des métiers réels chargés pour ce pays. Les autres pays n'ont aucune donnée : ni métier, ni compétence, ni marché du travail.</p>
          <p class="note atlas-next">Le référentiel international de l'OIT (ISCO) n'est pas encore branché : chaque pays couvert jusqu'ici repose sur sa propre nomenclature. C'est le prochain chantier.</p>
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