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
    data: jsonb("data").$type<Record<string, unknown>>().notNull().default({}),
  },
  (t) => [primaryKey({ columns: [t.id, t.version] }), index("occupation_version_idx").on(t.version)],
);

export const formation = pgTable(
  "formation",
  {
    id: text("id").notNull(),
    version: text("version").notNull(),
    title: text("title"),
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
