import { BasePlugin } from "~/types/BasePlugin";
import z from "zod";
import { FastifyPluginAsync } from "fastify";

const responseSchema = z.object({
  message: z.string(),
});

export const route: FastifyPluginAsync = async (fastify, opts) => {
  // GET /restaurant
  fastify.route({
    method: "GET",
    url: "/",
    schema: {
      response: {
        200: responseSchema,
      },
    },
    handler: async (req, res) => {
      return { message: "hej" };
    },
  });
};

export default route;
