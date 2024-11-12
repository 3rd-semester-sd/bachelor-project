import { BasePlugin } from "~/types/BasePlugin";
import z from "zod";
import { FastifyPluginAsync } from "fastify";
import { usersTable } from "~/db/schema";

const responseSchema = z.object({
  message: z.string(),
});

export const route: FastifyPluginAsync = async (fastify, opts) => {
  // GET /restaurant
  fastify.route({
    method: "GET",
    url: "/",
    schema: {
      tags: ["Restaurant"],
      response: {
        200: responseSchema,
      },
    },
    handler: async (req, res) => {
      const test = await fastify.db.select().from(usersTable).limit(10);
      console.log(test);
      return { message: "hej" };
    },
  });
};

export default route;
