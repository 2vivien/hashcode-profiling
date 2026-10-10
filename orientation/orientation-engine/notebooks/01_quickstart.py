# %%
# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # Moteur d'orientation — exploration rapide
#
# Notebook sandbox pour **développer et déboguer les algorithmes** sans passer
# par l'API. Ouvrir avec JupyterLab (jupytext convertit ce `.py` en notebook).
#
# Lancement : `make sandbox` puis http://localhost:8888

# %%
from pathlib import Path

from orientation.application.use_cases.generate_recommendation import GenerateRecommendation
from orientation.contracts.profile import StudentProfile

data_root = Path("/app/data/knowledge/v1")
engine = GenerateRecommendation(data_root)

# %% [markdown]
# ## 1. Construire un profil conforme au contrat

# %%
profile = StudentProfile(
    student_id="nb-demo",
    interests={"investigative": 0.8, "realistic": 0.7, "conventional": 0.6},
    abilities={"logical": 0.9, "verbal": 0.5},
    subjects={"mathematics": 0.8, "computer_science": 0.9},
    skills=[
        {"skill_id": "programming", "level": 0.8, "confidence": 0.7,
         "source": "declared", "status": "declared"},
    ],
)
profile

# %% [markdown]
# ## 2. Exécuter le pipeline complet

# %%
rec = engine.execute(profile)
print("modèle:", rec.model_version, "| connaissance:", rec.knowledge_version)
for item in rec.candidates:
    print(f"{item.direction_name:24} score={item.score:.3f} "
          f"conf={item.confidence:.3f} incert={item.uncertainty:.3f}")

# %% [markdown]
# ## 3. Inspecter la décomposition et les gaps

# %%
item = rec.candidates[0]
item.score_breakdown.model_dump()

# %%
[g.model_dump() for g in item.skill_gaps]

# %% [markdown]
# ## 4. Explorer une variante de pondération
#
# Modifier un poids dans `RecommendationConfig`, relancer, comparer —
# c'est ici qu'on développe/valide les algorithmes.

# %%
from orientation.config.recommendation import RecommendationConfig

cfg = RecommendationConfig()
cfg.validate()
cfg.model_dump()
