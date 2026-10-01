from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IscoMajorGroup:
    code: str
    name_fr: str
    name_en: str
    description_fr: str


ISCO_MAJOR_GROUPS: tuple[IscoMajorGroup, ...] = (
    IscoMajorGroup("0", "Professions des forces armées", "Armed forces occupations", "Défense et fonctions militaires."),
    IscoMajorGroup("1", "Directeurs, cadres de direction et gérants", "Managers", "Direction, gestion et pilotage des organisations."),
    IscoMajorGroup("2", "Professions intellectuelles et scientifiques", "Professionals", "Professions nécessitant généralement un haut niveau de connaissances spécialisées."),
    IscoMajorGroup("3", "Professions intermédiaires", "Technicians and associate professionals", "Métiers techniques, opérationnels et professions intermédiaires spécialisées."),
    IscoMajorGroup("4", "Employés de type administratif", "Clerical support workers", "Administration, secrétariat, traitement de l'information et support de bureau."),
    IscoMajorGroup("5", "Personnel des services directs aux particuliers, commerçants et vendeurs", "Service and sales workers", "Services, vente, relation client et commerce."),
    IscoMajorGroup("6", "Agriculteurs et ouvriers qualifiés de l'agriculture, de la sylviculture et de la pêche", "Skilled agricultural, forestry and fishery workers", "Production agricole, élevage, sylviculture et pêche."),
    IscoMajorGroup("7", "Métiers qualifiés de l'industrie et de l'artisanat", "Craft and related trades workers", "Construction, maintenance, fabrication et artisanat qualifié."),
    IscoMajorGroup("8", "Conducteurs d'installations et de machines, et ouvriers de l'assemblage", "Plant and machine operators and assemblers", "Conduite d'équipements, machines, procédés industriels et assemblage."),
    IscoMajorGroup("9", "Professions élémentaires", "Elementary occupations", "Travaux d'exécution et activités nécessitant un niveau de compétences élémentaire."),
)


def major_group(code: str | None) -> IscoMajorGroup | None:
    if not code:
        return None
    return next((item for item in ISCO_MAJOR_GROUPS if item.code == code[:1]), None)
