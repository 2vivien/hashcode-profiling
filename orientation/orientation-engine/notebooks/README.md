# Notebooks / Sandbox

Espace d'exploration pour **développer, déboguer et valider les algorithmes**
sans passer par l'API HTTP.

## Lancer le sandbox

```bash
make sandbox        # → http://localhost:8888
```

Le service `jupyter` (profil Docker `dev`) monte ce dossier, `src/` et `data/`,
et installe l'outillage scientifique (`requirements-notebooks.txt`).

## Fichiers

- `01_quickstart.py` — profil → pipeline → décomposition. Format **jupytext
  percent** : JupyterLab l'ouvre comme un notebook (et le diff reste lisible en Git).

## Bonnes pratiques

- Les notebooks **ne font pas partie de la production** (image `Dockerfile`).
- Convertir/valider en CI : `nbqa ruff notebooks/` et `jupytext --to ipynb`.
- Tout résultat validé doit finir en **test** (`tests/`) et non rester en notebook.
