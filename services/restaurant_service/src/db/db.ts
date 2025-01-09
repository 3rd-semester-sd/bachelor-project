import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "~/db/schema";
import { migrate } from "drizzle-orm/postgres-js/migrator";

export async function getDbClient(db_url: string) {
  const sql = postgres(db_url, {
    ssl: {
      rejectUnauthorized: false,
    },
  });
  const db = drizzle(sql, { schema });

  return db;
}

export type DbClient = Awaited<ReturnType<typeof getDbClient>>;

export async function migrateDatabase(db: DbClient) {
  // Run migrations
  await migrate(db, { migrationsFolder: "./drizzle" });
}