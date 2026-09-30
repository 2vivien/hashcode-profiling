# Mathématiques du moteur

## Normalisation

Z-score :

    z = (x - μ) / σ

Min-max :

    x' = (x - xmin) / (xmax - xmin)

Le choix dépend de la distribution et de la sémantique.

## Similarité cosinus

    cos(x,y) = (x·y) / (||x|| ||y||)

Utilisable pour :

- intérêts ;
- compétences ;
- embeddings ;
- descriptions.

## Cosinus pondéré

    S(x,y) =
      Σ w_i c_i x_i y_i
      /
      sqrt(Σ w_i c_i x_i²) sqrt(Σ w_i c_i y_i²)

c_i représente la confiance du signal.

## Distance euclidienne

    D(x,y) = sqrt(Σ w_i (x_i-y_i)²)

## Distance de Mahalanobis

    D_M(x,y) =
      sqrt((x-y)^T Σ^-1 (x-y))

Elle tient compte des corrélations entre variables.

Sur petits échantillons, Σ doit être stabilisée/régularisée.

## Score multidimensionnel

Pour une direction d :

    S_d =
      wI*InterestFit
      + wA*AbilityFit
      + wS*SkillFit
      + wV*ValueFit
      + wE*EnvironmentFit
      + wT*TrajectoryFit
      + wSE*SelfEfficacy
      + wCA*Adaptability
      - wG*SkillGap

Les poids sont des hypothèses expérimentales tant qu'ils ne sont pas validés.

## Confiance

    w_eff = w * confidence

Une donnée très incertaine doit peser moins qu'une donnée solidement observée.

## Skill gap

    G_k = max(0, Required_k - Observed_k)

Présentation :

    « compétence à renforcer »

et non :

    « tu n'es pas capable ».

## Statistiques de trajectoire

Moyenne :

    x̄ = (1/n) Σ x_i

Variance :

    Var(X) = (1/(n-1)) Σ(x_i-x̄)²

Vélocité :

    v_t = x_t - x_(t-1)

Accélération :

    a_t = v_t - v_(t-1)

Tendance :

    y_t = β0 + β1 t + ε_t

## Entropie

    H(X) = -Σ p_i log p_i

Une entropie élevée peut signaler un profil encore très ouvert.

## Diversification — MMR

    MMR(d) =
      λ Rel(d)
      - (1-λ) max Sim(d,d')

Le moteur évite ainsi de proposer dix variantes presque identiques.

## Contrefactuel

Si :

    score = f(profile)

chercher une modification :

    Δprofile

telle que :

    f(profile + Δprofile) ≥ seuil

Le résultat doit rester une simulation du modèle, pas une causalité réelle.

## Bayesian updating

    P(H|D) ∝ P(D|H)P(H)

Utilisation :

- représenter l'incertitude ;
- mettre à jour une hypothèse ;
- éviter les décisions binaires.

## Principe

Le moteur peut être mathématiquement sophistiqué tout en restant explicable.

Il ne faut jamais confondre sophistication mathématique et validité scientifique.
