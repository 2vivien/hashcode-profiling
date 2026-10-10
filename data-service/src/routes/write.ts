import { z } from "zod";
import { eq } from "drizzle-orm";

import { db } from "../db/client.js";
import { feedback, observation, auditEvent, profile, recommendation, recommendationItem } from "../db/schema.js";

const dimensionsSchema = z.record(z.string(), z.record(z.string(), z.number()));

const profileBody = z.object({
  studentRef: z.string().min(1),
  profileVersion: z.string().min(1),
  assessmentConfidence: z.number().min(0).max(1).optional(),
  dimensions: dimensionsSchema,
  constraints: z.record(z.string(), z.unknown()).default({}),
});

const recommendationBody = z.object({
  id: z.string().min(1),
  studentRef: z.string().min(1),
  profileVersion: z.string().min(1),
  modelVersion: z.string().min(1),
  knowledgeVersion: z.string().min(1),
  audit: z.record(z.string(), z.unknown()).default({}),
  items: z
    .array(
      z.object({
        directionId: z.string().min(1),
        rank: z.number().int(),
        score: z.number(),
        confidence: z.number(),
        uncertainty: z.number(),
        payload: z.record(z.string(), z.unknown()).default({}),
      }),
    )
    .default([]),
});

const feedbackBody = z.object({
  studentRef: z.string().min(1),
  directionId: z.string().min(1),
  type: z.string().min(1),
  payload: z.record(z.string(), z.unknown()).default({}),
});

export async function postProfile(body: unknown) {
  const parsed = profileBody.safeParse(body);
  if (!parsed.success) {
    return { status: 422, payload: { detail: parsed.error.issues } };
  }
  const data = parsed.data;
  await db
    .insert(profile)
    .values({
      studentRef: data.studentRef,
      profileVersion: data.profileVersion,
      dimensions: data.dimensions,
      constraints: data.constraints,
    })
    .onConflictDoUpdate({
      target: [profile.studentRef, profile.profileVersion],
      set: { dimensions: data.dimensions, constraints: data.constraints },
    });
  return { status: 201, payload: { ok: true } };
}

export async function postRecommendation(body: unknown) {
  const parsed = recommendationBody.safeParse(body);
  if (!parsed.success) {
    return { status: 422, payload: { detail: parsed.error.issues } };
  }
  const data = parsed.data;
  await db
    .insert(recommendation)
    .values({
      id: data.id,
      studentRef: data.studentRef,
      profileVersion: data.profileVersion,
      modelVersion: data.modelVersion,
      knowledgeVersion: data.knowledgeVersion,
      audit: data.audit,
    })
    .onConflictDoUpdate({
      target: recommendation.id,
      set: {
        modelVersion: data.modelVersion,
        knowledgeVersion: data.knowledgeVersion,
        audit: data.audit,
      },
    });

  await db.delete(recommendationItem).where(eq(recommendationItem.recommendationId, data.id));
  if (data.items.length > 0) {
    await db.insert(recommendationItem).values(
      data.items.map((item) => ({
        recommendationId: data.id,
        directionId: item.directionId,
        rank: item.rank,
        score: item.score,
        confidence: item.confidence,
        uncertainty: item.uncertainty,
        payload: item.payload,
      })),
    );
  }
  return { status: 201, payload: { ok: true } };
}

export async function postFeedback(body: unknown) {
  const parsed = feedbackBody.safeParse(body);
  if (!parsed.success) {
    return { status: 422, payload: { detail: parsed.error.issues } };
  }
  const data = parsed.data;
  await db.insert(feedback).values({
    studentRef: data.studentRef,
    directionId: data.directionId,
    type: data.type,
    payload: data.payload,
  });
  return { status: 201, payload: { ok: true } };
}

const observationBody = z.object({
  observations: z.array(
    z.object({
      studentRef: z.string().min(1),
      dimension: z.string().min(1),
      value: z.unknown(),
      confidence: z.number().min(0).max(1),
      source: z.string().min(1),
      state: z.string().min(1),
      observedAt: z.string().nullish(),
    }),
  ),
});

const auditEventBody = z.object({
  events: z.array(
    z.object({
      recommendationId: z.string().optional(),
      studentRef: z.string().optional(),
      eventType: z.string().min(1),
      detail: z.record(z.string(), z.unknown()).default({}),
    }),
  ),
});

export async function postObservations(body: unknown) {
  const parsed = observationBody.safeParse(body);
  if (!parsed.success) {
    return { status: 422, payload: { detail: parsed.error.issues } };
  }
  const rows = parsed.data.observations;
  if (rows.length > 0) {
    await db.insert(observation).values(
      rows.map((o) => ({
        studentRef: o.studentRef,
        dimension: o.dimension,
        value: o.value,
        confidence: o.confidence,
        source: o.source,
        state: o.state,
        observedAt: o.observedAt ? new Date(o.observedAt) : new Date(),
      })),
    );
  }
  return { status: 201, payload: { ok: true, count: rows.length } };
}

export async function postAuditEvents(body: unknown) {
  const parsed = auditEventBody.safeParse(body);
  if (!parsed.success) {
    return { status: 422, payload: { detail: parsed.error.issues } };
  }
  const rows = parsed.data.events;
  if (rows.length > 0) {
    await db.insert(auditEvent).values(
      rows.map((e) => ({
        recommendationId: e.recommendationId ?? null,
        studentRef: e.studentRef ?? null,
        eventType: e.eventType,
        detail: e.detail,
      })),
    );
  }
  return { status: 201, payload: { ok: true, count: rows.length } };
}

export async function getProfile(studentRef: string) {
  const rows = await db
    .select()
    .from(profile)
    .where(eq(profile.studentRef, studentRef))
    .orderBy(profile.createdAt);
  const latest = rows[rows.length - 1];
  return latest ? { status: 200, payload: latest } : { status: 404, payload: { detail: "not found" } };
}