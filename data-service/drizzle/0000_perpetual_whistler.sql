CREATE TABLE "audit_event" (
	"id" serial PRIMARY KEY NOT NULL,
	"recommendation_id" text,
	"student_ref" text,
	"event_type" text NOT NULL,
	"detail" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "direction" (
	"id" text NOT NULL,
	"version" text NOT NULL,
	"canonical_name" text NOT NULL,
	"taxonomy" text NOT NULL,
	"aliases" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"interests" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"abilities" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"skills" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"subjects" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"values" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"data" jsonb DEFAULT '{}'::jsonb NOT NULL,
	CONSTRAINT "direction_id_version_pk" PRIMARY KEY("id","version")
);
--> statement-breakpoint
CREATE TABLE "feedback" (
	"id" serial PRIMARY KEY NOT NULL,
	"student_ref" text NOT NULL,
	"direction_id" text NOT NULL,
	"type" text NOT NULL,
	"payload" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "formation" (
	"id" text NOT NULL,
	"version" text NOT NULL,
	"title" text,
	"data" jsonb DEFAULT '{}'::jsonb NOT NULL,
	CONSTRAINT "formation_id_version_pk" PRIMARY KEY("id","version")
);
--> statement-breakpoint
CREATE TABLE "knowledge_version" (
	"id" serial PRIMARY KEY NOT NULL,
	"version" text NOT NULL,
	"source" text,
	"status" text DEFAULT 'active' NOT NULL,
	"manifest" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "knowledge_version_version_unique" UNIQUE("version")
);
--> statement-breakpoint
CREATE TABLE "mapping" (
	"id" serial PRIMARY KEY NOT NULL,
	"version" text NOT NULL,
	"source_id" text NOT NULL,
	"target_id" text NOT NULL,
	"relation" text NOT NULL,
	"weight" real,
	"data" jsonb DEFAULT '{}'::jsonb NOT NULL
);
--> statement-breakpoint
CREATE TABLE "model_registry" (
	"id" serial PRIMARY KEY NOT NULL,
	"task" text NOT NULL,
	"model_version" text NOT NULL,
	"training_data_version" text,
	"features" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"metrics" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"status" text DEFAULT 'experimental' NOT NULL,
	"active" boolean DEFAULT false NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "observation" (
	"id" serial PRIMARY KEY NOT NULL,
	"student_ref" text NOT NULL,
	"dimension" text NOT NULL,
	"value" jsonb,
	"confidence" real DEFAULT 0 NOT NULL,
	"source" text NOT NULL,
	"state" text DEFAULT 'known' NOT NULL,
	"observed_at" timestamp with time zone DEFAULT now() NOT NULL,
	"version" text DEFAULT 'v1' NOT NULL
);
--> statement-breakpoint
CREATE TABLE "occupation" (
	"id" text NOT NULL,
	"version" text NOT NULL,
	"title" text,
	"source" text,
	"isco08_code" text,
	"data" jsonb DEFAULT '{}'::jsonb NOT NULL,
	CONSTRAINT "occupation_id_version_pk" PRIMARY KEY("id","version")
);
--> statement-breakpoint
CREATE TABLE "profile" (
	"id" serial PRIMARY KEY NOT NULL,
	"student_ref" text NOT NULL,
	"profile_version" text DEFAULT 'v1' NOT NULL,
	"dimensions" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"constraints" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "recommendation" (
	"id" text PRIMARY KEY NOT NULL,
	"student_ref" text NOT NULL,
	"profile_version" text NOT NULL,
	"model_version" text NOT NULL,
	"knowledge_version" text NOT NULL,
	"audit" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "recommendation_item" (
	"id" serial PRIMARY KEY NOT NULL,
	"recommendation_id" text NOT NULL,
	"direction_id" text NOT NULL,
	"rank" integer NOT NULL,
	"score" real NOT NULL,
	"confidence" real NOT NULL,
	"uncertainty" real NOT NULL,
	"payload" jsonb DEFAULT '{}'::jsonb NOT NULL
);
--> statement-breakpoint
CREATE TABLE "skill" (
	"id" text NOT NULL,
	"version" text NOT NULL,
	"label" text,
	"data" jsonb DEFAULT '{}'::jsonb NOT NULL,
	CONSTRAINT "skill_id_version_pk" PRIMARY KEY("id","version")
);
--> statement-breakpoint
CREATE INDEX "direction_version_idx" ON "direction" USING btree ("version");--> statement-breakpoint
CREATE INDEX "feedback_student_idx" ON "feedback" USING btree ("student_ref");--> statement-breakpoint
CREATE INDEX "mapping_version_idx" ON "mapping" USING btree ("version");--> statement-breakpoint
CREATE INDEX "mapping_source_idx" ON "mapping" USING btree ("source_id");--> statement-breakpoint
CREATE INDEX "observation_student_idx" ON "observation" USING btree ("student_ref");--> statement-breakpoint
CREATE INDEX "occupation_version_idx" ON "occupation" USING btree ("version");--> statement-breakpoint
CREATE UNIQUE INDEX "profile_student_version_idx" ON "profile" USING btree ("student_ref","profile_version");--> statement-breakpoint
CREATE INDEX "recommendation_student_idx" ON "recommendation" USING btree ("student_ref");--> statement-breakpoint
CREATE INDEX "recommendation_item_rec_idx" ON "recommendation_item" USING btree ("recommendation_id");