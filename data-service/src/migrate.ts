import { migrate } from "drizzle-orm/node-postgres/migrator";

import { db, pool } from "./db/client.js";

const folder = process.env.MIGRATIONS_DIR ?? "./drizzle";

await migrate(db, { migrationsFolder: folder });
await pool.end();
console.log(`[migrate] migrations appliquées depuis ${folder}`);
