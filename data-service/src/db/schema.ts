import {
  boolean,
  index,
  integer,
  jsonb,
  pgTable,
  primaryKey,
  real,
  serial,
  text,
  timestamp,
  uniqueIndex,
} from "drizzle-orm/pg-core";

/**
 * Source de vérité de la connaissance et des données du moteur.
 * Toute évolution passe par une migration (drizzle-kit generate).
 */

export const knowledgeVersion = pgTable("knowledge_version", {
  id: serial("id").primaryKey(),
  version: text("version").notNull().unique(),
  source: text("source"),
  status: text("status").notNull().default("active"),
  manifest: jsonb("manifest").$type<Record<string, unknown>>().notNull().default({}),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
});

export const direction = pgTable(
  "direction",
  {
    id: text("id").notNull(),
    version: text("version").notNull(),
    canonicalName: text("canonical_name").notNull(),
    taxonomy: text("taxonomy").notNull(),
    aliases: jsonb("aliases").$type<string[]>().notNull().default([]),
    interests: jsonb("interests").$type<Record<string, number>>().notNull().default({}),
    abilities: jsonb("abilities").$type<Record<string, number>>().notNull().default({}),
    skills: jsonb("skills").$type<Record<string, number>>().notNull().default({}),
    subjects: jsonb("subjects").$type<Record<string, number>>().notNull().default({}),
    values: jsonb("values").$type<Record<string, number>>().notNull().default({}),
    data: jsonb("data").$type<Record<string, unknown>>().notNull().default({}),
  },
  (t) => [primaryKey({ columns: [t.id, t.version] }), index("direction_version_idx").on(t.version)],
);

export const skill = pgTable(
  "skill",
  {
    id: text("id").notNull(),
    version: text("version").notNull(),
    label: text("label"),
    language: text("language").notNull().default("fr"),
    originalLabel: text("original_label"),
    translationStatus: text("translation_status").notNull().default("none"),
    data: jsonb("data").$type<Record<string, unknown>>().notNull().default({}),
  },
  (t) => [primaryKey({ columns: [t.id, t.version] })],
);

export const occupation = pgTable(
  "occupation",
  {
    id: text("id").notNull(),
    version: text("version").notNull(),
    title: text("title"),
    source: text("source"),
    isco08Code: text("isco08_code"),
    /** Langue du contenu de `title` (ISO 639-1). */
    language: text("language").notNull().default("fr"),
    /** Libellé d'origine avant traduction (null si la source est déjà en français). */
    originalTitle: text("original_title"),
    /** none | pending | done | failed | source */
    translationStatus: text("translation_status").notNull().default("none"),
    /** female | male | mixed | null — dénote le genre, jamais l'orientation d'une personne. */
    gender: text("gender"),
    /** Répartition observée sur le marché, ex. { "female": 0.42, "male": 0.58 }. */
    genderDistribution: jsonb("gender_distribution").$type<Record<string, number>>().notNull().default({}),
    data: jsonb("data").$type<Record<string, unknown>>().notNull().default({}),
  },
  (t) => [
    primaryKey({ columns: [t.id, t.version] }),
    index("occupation_version_idx").on(t.version),
    index("occupation_language_idx").on(t.language),
  ],
);

/**
 * Employeur : qui recrute, où, en combien.
 *
 * Volontairement **séparé** de `occupation` : un métier est une notion stable
 * et théorique, un emploi est une donnée qui bouge chaque semaine. Mélanger les
 * deux produirait des recommandations fausses au bout de trois mois.
 */
export const employer = pgTable(
  "employer",
  {
    id: text("id").notNull(),
    version: text("version").notNull(),
    name: text("name").notNull(),
    /** Secteur d'activité (NAF/ISIC ou code local). */
    activityCode: text("activity_code"),
    /** Identifiant national de l'organisation (SIREN, registre local...). */
    registryId: text("registry_id"),
    /** ISO 3166-1 alpha-3 du pays où l'employeur opère. */
    country: text("country").notNull().default("FR"),
    /** ISO 3166-2 ou code local de la subdivision. */
    region: text("region"),
    /** Code postal ou identifiant de localité. */
    locality: text("locality"),
    /** Effectif déclaré, si connu. */
    headcount: integer("headcount"),
    /** Nombre d'offres au moment de la collecte — périmé vite. */
    openings: integer("openings"),
    /** Métiers rattachés : occupation_id, plusieurs possibles. */
    occupationIds: jsonb("occupation_ids").$type<string[]>().notNull().default([]),
    /** Date de la collecte : sans elle, une ligne d'employeur n'est pas datable. */
    observedAt: timestamp("observed_at", { withTimezone: true }).notNull().defaultNow(),
    data: jsonb("data").$type<Record<string, unknown>>().notNull().default({}),
  },
  (t) => [
    primaryKey({ columns: [t.id, t.version] }),
    index("employer_version_idx").on(t.version),
    index("employer_country_idx").on(t.country),
  ],
);

/** Langues exigées ou valorisées par un métier (CEFR : A1..C2). */
export const languageRequirement = pgTable(
  "language_requirement",
  {
    occupationId: text("occupation_id").notNull(),
    version: text("version").notNull(),
    /** Code ISO 639-1, ex. "en". */
    languageCode: text("language_code").notNull(),
    /** Niveau CECRL attendu : A1..C2 ; null si non qualifié. */
    cefrLevel: text("cefr_level"),
    required: boolean("required").notNull().default(false),
    importance: real("importance"),
    data: jsonb("data").$type<Record<string, unknown>>().notNull().default({}),
  },
  (t) => [
    primaryKey({ columns: [t.occupationId, t.version, t.languageCode] }),
    index("language_requirement_occupation_idx").on(t.occupationId),
  ],
);

export const formation = pgTable(
  "formation",
  {
    id: text("id").notNull(),
    version: text("version").notNull(),
    title: text("title"),
    language: text("language").notNull().default("fr"),
    originalTitle: text("original_title"),
    translationStatus: text("translation_status").notNull().default("none"),
    /** Niveau CECRL de sortie visé, quand la formation est certifye. */
    cefrLevel: text("cefr_level"),
    data: jsonb("data").$type<Record<string, unknown>>().notNull().default({}),
  },
  (t) => [primaryKey({ columns: [t.id, t.version] })],
);

export const mapping = pgTable(
  "mapping",
  {
    id: serial("id").primaryKey(),
    version: text("version").notNull(),
    sourceId: text("source_id").notNull(),
    targetId: text("target_id").notNull(),
    relation: text("relation").notNull(),
    weight: real("weight"),
    data: jsonb("data").$type<Record<string, unknown>>().notNull().default({}),
  },
  (t) => [index("mapping_version_idx").on(t.version), index("mapping_source_idx").on(t.sourceId)],
);

/* ---------- Données produit / longitudinales (pseudonymisées) ---------- */

export const profile = pgTable(
  "profile",
  {
    id: serial("id").primaryKey(),
    studentRef: text("student_ref").notNull(),
    profileVersion: text("profile_version").notNull().default("v1"),
    dimensions: jsonb("dimensions").$type<Record<string, Record<string, number>>>().notNull().default({}),
    constraints: jsonb("constraints").$type<Record<string, unknown>>().notNull().default({}),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [uniqueIndex("profile_student_version_idx").on(t.studentRef, t.profileVersion)],
);

export const observation = pgTable(
  "observation",
  {
    id: serial("id").primaryKey(),
    studentRef: text("student_ref").notNull(),
    dimension: text("dimension").notNull(),
    value: jsonb("value").$type<unknown>(),
    confidence: real("confidence").notNull().default(0),
    source: text("source").notNull(),
    state: text("state").notNull().default("known"),
    observedAt: timestamp("observed_at", { withTimezone: true }).notNull().defaultNow(),
    version: text("version").notNull().default("v1"),
  },
  (t) => [index("observation_student_idx").on(t.studentRef)],
);

export const recommendation = pgTable(
  "recommendation",
  {
    id: text("id").primaryKey(),
    studentRef: text("student_ref").notNull(),
    profileVersion: text("profile_version").notNull(),
    modelVersion: text("model_version").notNull(),
    knowledgeVersion: text("knowledge_version").notNull(),
    audit: jsonb("audit").$type<Record<string, unknown>>().notNull().default({}),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [index("recommendation_student_idx").on(t.studentRef)],
);

export const recommendationItem = pgTable(
  "recommendation_item",
  {
    id: serial("id").primaryKey(),
    recommendationId: text("recommendation_id").notNull(),
    directionId: text("direction_id").notNull(),
    rank: integer("rank").notNull(),
    score: real("score").notNull(),
    confidence: real("confidence").notNull(),
    uncertainty: real("uncertainty").notNull(),
    payload: jsonb("payload").$type<Record<string, unknown>>().notNull().default({}),
  },
  (t) => [index("recommendation_item_rec_idx").on(t.recommendationId)],
);

export const feedback = pgTable(
  "feedback",
  {
    id: serial("id").primaryKey(),
    studentRef: text("student_ref").notNull(),
    directionId: text("direction_id").notNull(),
    type: text("type").notNull(),
    payload: jsonb("payload").$type<Record<string, unknown>>().notNull().default({}),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [index("feedback_student_idx").on(t.studentRef)],
);

export const auditEvent = pgTable("audit_event", {
  id: serial("id").primaryKey(),
  recommendationId: text("recommendation_id"),
  studentRef: text("student_ref"),
  eventType: text("event_type").notNull(),
  detail: jsonb("detail").$type<Record<string, unknown>>().notNull().default({}),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
});

export const modelRegistry = pgTable(
  "model_registry",
  {
    id: serial("id").primaryKey(),
    task: text("task").notNull(),
    modelVersion: text("model_version").notNull(),
    trainingDataVersion: text("training_data_version"),
    features: jsonb("features").$type<string[]>().notNull().default([]),
    metrics: jsonb("metrics").$type<Record<string, number>>().notNull().default({}),
    status: text("status").notNull().default("experimental"),
    active: boolean("active").notNull().default(false),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [uniqueIndex("model_registry_task_version_idx").on(t.task, t.modelVersion)],
);
