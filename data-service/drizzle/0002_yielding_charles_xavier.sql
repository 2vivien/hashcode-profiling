CREATE TABLE "language_requirement" (
	"occupation_id" text NOT NULL,
	"version" text NOT NULL,
	"language_code" text NOT NULL,
	"cefr_level" text,
	"required" boolean DEFAULT false NOT NULL,
	"importance" real,
	"data" jsonb DEFAULT '{}'::jsonb NOT NULL,
	CONSTRAINT "language_requirement_occupation_id_version_language_code_pk" PRIMARY KEY("occupation_id","version","language_code")
);
--> statement-breakpoint
ALTER TABLE "formation" ADD COLUMN "language" text DEFAULT 'fr' NOT NULL;--> statement-breakpoint
ALTER TABLE "formation" ADD COLUMN "original_title" text;--> statement-breakpoint
ALTER TABLE "formation" ADD COLUMN "translation_status" text DEFAULT 'none' NOT NULL;--> statement-breakpoint
ALTER TABLE "formation" ADD COLUMN "cefr_level" text;--> statement-breakpoint
ALTER TABLE "occupation" ADD COLUMN "language" text DEFAULT 'fr' NOT NULL;--> statement-breakpoint
ALTER TABLE "occupation" ADD COLUMN "original_title" text;--> statement-breakpoint
ALTER TABLE "occupation" ADD COLUMN "translation_status" text DEFAULT 'none' NOT NULL;--> statement-breakpoint
ALTER TABLE "occupation" ADD COLUMN "gender" text;--> statement-breakpoint
ALTER TABLE "occupation" ADD COLUMN "gender_distribution" jsonb DEFAULT '{}'::jsonb NOT NULL;--> statement-breakpoint
ALTER TABLE "skill" ADD COLUMN "language" text DEFAULT 'fr' NOT NULL;--> statement-breakpoint
ALTER TABLE "skill" ADD COLUMN "original_label" text;--> statement-breakpoint
ALTER TABLE "skill" ADD COLUMN "translation_status" text DEFAULT 'none' NOT NULL;--> statement-breakpoint
CREATE INDEX "language_requirement_occupation_idx" ON "language_requirement" USING btree ("occupation_id");--> statement-breakpoint
CREATE INDEX "occupation_language_idx" ON "occupation" USING btree ("language");