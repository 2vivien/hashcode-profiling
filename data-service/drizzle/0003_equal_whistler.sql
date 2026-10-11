CREATE TABLE "employer" (
	"id" text NOT NULL,
	"version" text NOT NULL,
	"name" text NOT NULL,
	"activity_code" text,
	"registry_id" text,
	"country" text DEFAULT 'FR' NOT NULL,
	"region" text,
	"locality" text,
	"headcount" integer,
	"openings" integer,
	"occupation_ids" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"observed_at" timestamp with time zone DEFAULT now() NOT NULL,
	"data" jsonb DEFAULT '{}'::jsonb NOT NULL,
	CONSTRAINT "employer_id_version_pk" PRIMARY KEY("id","version")
);
--> statement-breakpoint
CREATE INDEX "employer_version_idx" ON "employer" USING btree ("version");--> statement-breakpoint
CREATE INDEX "employer_country_idx" ON "employer" USING btree ("country");