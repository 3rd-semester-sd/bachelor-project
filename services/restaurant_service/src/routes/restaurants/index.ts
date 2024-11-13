import { BasePlugin } from "~/types/BasePlugin";
import z from "zod";
import { FastifyPluginAsync } from "fastify";
import { usersTable } from "~/db/schema";

const responseSchema = z.object({
  message: z.any(),
});

export const route: BasePlugin = async (fastify, opts) => {
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

      return res.send({ message: test });
    },
  });
};

export default route;
