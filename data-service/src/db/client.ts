import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";

import * as schema from "./schema.js";

const url = process.env.DATABASE_URL;
if (!url) {
  throw new Error("DATABASE_URL est requis pour le data-service");
}

export const pool = new Pool({ connectionString: url, max: 10 });
export const db = drizzle(pool, { schema });
export { schema };
