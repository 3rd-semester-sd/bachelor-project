import {
  DbClient,
  getDbClient,
  migrateDatabase,
  seedDatabaseTestData,
} from "~/db/db";
import { RawServerBase } from "fastify";
import { fastifyPlugin } from "fastify-plugin";
import { ZodTypeProvider } from "fastify-type-provider-zod";

declare module "fastify" {
  interface FastifyInstance {
    db: DbClient;
  }
}
export type DbPluginOptions = {
  databaseUrl: string;
};

export const dbPlugin = fastifyPlugin<
  DbPluginOptions,
  RawServerBase,
  ZodTypeProvider
>(async (fastify, { databaseUrl }) => {
  fastify.log.info(`[dbPlugin] Initializing db`);
  const db = await getDbClient(databaseUrl);
  await migrateDatabase(db);
  // await seedDatabaseTestData(db);
  fastify.decorate("db", db);
  fastify.db = db;
  fastify.log.info(`[dbPlugin] Initialized`);
});
