// Make sure to install the 'postgres' package
import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "~/db/schema";

export function getDbClient(db_url: string) {
  const queryClient = postgres(db_url);
  const db = drizzle(queryClient, { schema });
  return db;
}

export type DbClient = ReturnType<typeof getDbClient>;
