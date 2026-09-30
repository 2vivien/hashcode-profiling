from orientation.contracts.skill import SkillRequirement


class SkillTaxonomy:
    def normalize(self, requirements: list[SkillRequirement]) -> dict[str, float]:
        return {item.skill_id: item.required_level for item in requirements}
