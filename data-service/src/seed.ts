import { readFile } from "node:fs/promises";
import { join } from "node:path";

import { count, eq } from "drizzle-orm";

import { db, pool } from "./db/client.js";
import {
  direction,
  formation,
  knowledgeVersion,
  languageRequirement,
  mapping,
  modelRegistry,
  occupation,
  skill,
} from "./db/schema.js";

const dir = process.env.KNOWLEDGE_DIR ?? "/seed/knowledge/v1";

async function readJson<T>(file: string): Promise<T> {
  return JSON.parse(await readFile(join(dir, file), "utf8")) as T;
}

type Manifest = {
  version: string;
  source?: string;
  sha256?: string;
  item_counts?: Record<string, number>;
};

type RawDirection = {
  direction_id: string;
  canonical_name: string;
  taxonomy: string;
  aliases?: string[];
  interests?: Record<string, number>;
  abilities?: Record<string, number>;
  skills?: Record<string, number>;
  subjects?: Record<string, number>;
  values?: Record<string, number>;
} & Record<string, unknown>;

const manifest = await readJson<Manifest>("manifest.json");
const version = manifest.version;

// 1. Version de connaissance
await db
  .insert(knowledgeVersion)
  .values({
    version,
    source: manifest.source ?? null,
    status: "active",
    manifest: manifest as unknown as Record<string, unknown>,
  })
  .onConflictDoUpdate({
    target: knowledgeVersion.version,
    set: {
      source: manifest.source ?? null,
      manifest: manifest as unknown as Record<string, unknown>,
    },
  });

// 2. Directions
const directions = await readJson<RawDirection[]>("directions.json");
for (const d of directions) {
  const row = {
    id: d.direction_id,
    version,
    canonicalName: d.canonical_name,
    taxonomy: d.taxonomy,
    aliases: d.aliases ?? [],
    interests: d.interests ?? {},
    abilities: d.abilities ?? {},
    skills: d.skills ?? {},
    subjects: d.subjects ?? {},
    values: d.values ?? {},
    data: d as unknown as Record<string, unknown>,
  };
  await db
    .insert(direction)
    .values(row)
    .onConflictDoUpdate({ target: [direction.id, direction.version], set: row });
}

// 3. Compétences (liste d'identifiants dans v1)
const skills = await readJson<string[]>("skills.json");
for (const id of skills) {
  await db
    .insert(skill)
    .values({ id, version, label: id, language: "fr", translationStatus: "source", data: {} })
    .onConflictDoNothing({ target: [skill.id, skill.version] });
}

// 4. Occupations / formations / mappings (présents à partir de v2)
type JsonRecord = Record<string, unknown>;

async function readOptional<T>(file: string): Promise<T | null> {
  try {
    return await readJson<T>(file);
  } catch {
    return null;
  }
}

const occupations = (await readOptional<JsonRecord[]>("occupations.json")) ?? [];
// Synchronisation complète de la version : on purge avant de réinsérer (seed idempotent).
await db.delete(occupation).where(eq(occupation.version, version));
for (const o of occupations) {
  // Genre : le champ peut venir du JSON de connaissance ou n'être porté que par `data`.
  const inner = (o.data as JsonRecord | undefined) ?? {};
  const gender = (o.gender as string | undefined) ?? (inner.gender as string | undefined) ?? null;
  const genderDistribution =
    (o.gender_distribution as Record<string, number> | undefined) ??
    (inner.gender_distribution as Record<string, number> | undefined) ??
    {};
  const row = {
    id: String(o.occupation_id ?? ""),
    version,
    title: (o.title as string) ?? null,
    source: (o.source as string) ?? null,
    isco08Code: (o.isco08_code as string) ?? null,
    language: (o.language as string) ?? "fr",
    originalTitle: (o.original_title as string) ?? null,
    translationStatus: (o.translation_status as string) ?? "none",
    gender,
    genderDistribution,
    data: o,
  };
  await db
    .insert(occupation)
    .values(row)
    .onConflictDoUpdate({ target: [occupation.id, occupation.version], set: row });
}

// Langues exigées / valorisées par métier (table dédiée : une ligne par langue).
const languageRequirements = (await readOptional<JsonRecord[]>("language_requirements.json")) ?? [];
await db.delete(languageRequirement).where(eq(languageRequirement.version, version));
for (const r of languageRequirements) {
  const occupationId = String(r.occupation_id ?? "");
  if (!occupationId) continue;
  await db.insert(languageRequirement).values({
    occupationId,
    version,
    languageCode: String(r.language_code ?? ""),
    cefrLevel: (r.cefr_level as string) ?? null,
    required: r.required === true,
    importance: typeof r.importance === "number" ? r.importance : null,
    data: r,
  });
}

const formations = (await readOptional<JsonRecord[]>("formations.json")) ?? [];
await db.delete(formation).where(eq(formation.version, version));
for (const f of formations) {
  const row = {
    id: String(f.formation_id ?? ""),
    version,
    title: (f.title as string) ?? null,
    language: (f.language as string) ?? "fr",
    originalTitle: (f.original_title as string) ?? null,
    translationStatus: (f.translation_status as string) ?? "none",
    cefrLevel: (f.cefr_level as string) ?? null,
    data: f,
  };
  await db
    .insert(formation)
    .values(row)
    .onConflictDoUpdate({ target: [formation.id, formation.version], set: row });
}

const mappings = (await readOptional<JsonRecord[]>("mappings.json")) ?? [];
await db.delete(mapping).where(eq(mapping.version, version));
for (const m of mappings) {
  await db.insert(mapping).values({
    version,
    sourceId: String(m.source_id ?? ""),
    targetId: String(m.target_id ?? ""),
    relation: String(m.relation ?? "related"),
    weight: typeof m.weight === "number" ? m.weight : null,
    data: m,
  });
}

// 6. Registre des modeles : baseline deterministe (toujours declare, meme sans dataset)
await db
  .insert(modelRegistry)
  .values({
    task: "recommendation",
    modelVersion: "deterministic-baseline-v1",
    trainingDataVersion: `knowledge-${version}`,
    features: [
      "interest_fit",
      "ability_fit",
      "skill_fit",
      "value_fit",
      "subject_fit",
      "self_efficacy_fit",
      "adaptability_fit",
      "environment_fit",
      "trajectory_fit",
      "semantic_fit",
      "graph_fit",
      "evidence",
      "skill_gap_penalty",
    ],
    metrics: {},
    status: "active",
    active: true,
  })
  .onConflictDoNothing({ target: [modelRegistry.task, modelRegistry.modelVersion] });

// 7. Contrôle
const counts = await db
  .select({ value: count() })
  .from(direction)
  .where(eq(direction.version, version));
const dirCount = counts[0]?.value ?? 0;

console.log(
  `[seed] version=${version} directions=${dirCount} skills=${skills.length} ` +
    `occupations=${occupations.length} formations=${formations.length} mappings=${mappings.length} ` +
    `language_requirements=${languageRequirements.length}`,
);

await pool.end();
