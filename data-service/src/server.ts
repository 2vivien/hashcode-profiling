import Fastify from "fastify";
import { desc, eq } from "drizzle-orm";

import { db, pool } from "./db/client.js";
import { direction, formation, knowledgeVersion, occupation, skill } from "./db/schema.js";
import { getProfile, postFeedback, postProfile, postRecommendation } from "./routes/write.js";
const app = Fastify({ logger: true });

app.get("/health", async () => {
  try {
    await pool.query("select 1");
    return { status: "ok", service: "hashcodeprofiling-data-service", database: true };
  } catch {
    return { status: "degraded", service: "hashcodeprofiling-data-service", database: false };
  }
});

app.get("/knowledge/versions", async () => {
  return db.select().from(knowledgeVersion).orderBy(desc(knowledgeVersion.createdAt));
});

app.get<{ Querystring: { version?: string } }>("/knowledge/directions", async (req) => {
  const version = req.query.version;
  const query = db.select().from(direction);
  return version ? query.where(eq(direction.version, version)) : query;
});

app.get<{ Querystring: { version?: string } }>("/knowledge/skills", async (req) => {
  const version = req.query.version;
  const query = db.select().from(skill);
  return version ? query.where(eq(skill.version, version)) : query;
});

app.get<{ Querystring: { version?: string } }>("/knowledge/occupations", async (req) => {
  const version = req.query.version;
  const query = db.select().from(occupation);
  return version ? query.where(eq(occupation.version, version)) : query;
});

app.get<{ Querystring: { version?: string } }>("/knowledge/formations", async (req) => {
  const version = req.query.version;
  const query = db.select().from(formation);
  return version ? query.where(eq(formation.version, version)) : query;
});

/* ---------- Écriture (moteur → base) ---------- */

app.post("/profiles", async (req, reply) => {
  const { status, payload } = await postProfile(req.body);
  return reply.code(status).send(payload);
});

app.post("/recommendations", async (req, reply) => {
  const { status, payload } = await postRecommendation(req.body);
  return reply.code(status).send(payload);
});

app.post("/feedback", async (req, reply) => {
  const { status, payload } = await postFeedback(req.body);
  return reply.code(status).send(payload);
});

app.get<{ Params: { studentRef: string } }>("/profiles/:studentRef", async (req, reply) => {
  const { status, payload } = await getProfile(req.params.studentRef);
  return reply.code(status).send(payload);
});

const port = Number(process.env.PORT ?? 4100);
await app.listen({ host: "0.0.0.0", port });
