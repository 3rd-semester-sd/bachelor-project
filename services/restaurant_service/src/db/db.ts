import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "~/db/schema";

export function getDbClient(db_url: string) {
  const sql = postgres(db_url);
  const db = drizzle(sql, { schema });
  return db;
}

export type DbClient = ReturnType<typeof getDbClient>;
