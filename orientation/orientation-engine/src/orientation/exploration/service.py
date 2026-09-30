from orientation.contracts.exploration import ExplorationIdea
from orientation.contracts.recommendation import RecommendationItem

class ExplorationService:
    def ideas(self,item: RecommendationItem) -> list[ExplorationIdea]:
        ideas = [
            ExplorationIdea(exploration_id=f"{item.direction_id}-project",kind="mini_project",title=f"Mini-projet lié à {item.direction_name}",purpose="Tester l'intérêt par une expérience concrète",related_dimensions=["interests","skills"]),
            ExplorationIdea(exploration_id=f"{item.direction_id}-discovery",kind="content",title=f"Découvrir une activité de {item.direction_name}",purpose="Obtenir une nouvelle observation du profil",related_dimensions=["interests"]),
        ]
        if item.skill_gaps:
            ideas.append(ExplorationIdea(exploration_id=f"{item.direction_id}-skill",kind="exercise",title="Exercice sur une compétence à renforcer",purpose="Mesurer une nouvelle observation de compétence",related_dimensions=["skills"]))
        return ideas
