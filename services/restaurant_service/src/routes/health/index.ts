import { BasePlugin } from "~/types/BasePlugin";
import { defaultResponseDTO } from "~/dtos/response_dtos";
import { z } from "zod";

export const route: BasePlugin = async (fastify, opts) => {
  fastify.route({
    method: "GET",
    url: "",
    schema: {
      tags: ["Restaurant"],
      response: {
        200: defaultResponseDTO,
        500: z.object({ error: z.string() }),
      },
    },
    handler: async (req, res) => {
      return res.send({ message: "ok" });
    },
  });
};

export default route;
