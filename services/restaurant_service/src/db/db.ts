import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "~/db/schema";
import { migrate } from "drizzle-orm/postgres-js/migrator";
import { main as seedDatabase } from "~/db/seed/seed"; // Import the seed script
import { count } from "drizzle-orm";

export async function getDbClient(db_url: string) {
  const sql = postgres(db_url);
  const db = drizzle(sql, { schema });

  return db;
}

export type DbClient = Awaited<ReturnType<typeof getDbClient>>;

export async function migrateDatabase(db: DbClient) {
  // Run migrations
  await migrate(db, { migrationsFolder: "./drizzle" });
}

export async function seedDatabaseTestData(db: DbClient) {
  // Check if the environment is development
  if (process.env.NODE_ENV !== "DEV") {
    console.log("Skipping database seeding: Not in development environment.");
    return;
  }

  // Check if the database is empty
  const [userCount] = await Promise.all([
    db.select({ count: count() }).from(schema.restaurantMembersTable),
    // db.select({ count: count() }).from(schema.restaurantsTable),
    // db.select({ count: count() }).from(schema.menusTable),
  ]);

  console.log(userCount);
  if (
    userCount[0].count > 0
    // restaurantCount[0].count > 0 ||
    // menuCount[0].count > 0
  ) {
    console.log("Skipping database seeding: Tables already contain data.");
    return;
  }

  console.log("Seeding database with test data...");
  await seedDatabase();
  console.log("Database seeding completed!");
}
