import { BasePlugin } from "~/types/BasePlugin";
import z from "zod";
import { FastifyPluginAsync } from "fastify";
import { usersTable, User, restaurantsTable } from "~/db/schema";
import { DataListResponseSchema } from "~/dtos/response_dtos";
import { RestaurantDTO } from "~/dtos/restaurant_dtos";

export const route: BasePlugin = async (fastify, opts) => {
  // GET /restaurant
  fastify.route({
    method: "GET",
    url: "/",
    schema: {
      tags: ["Restaurant"],
      response: {
        200: DataListResponseSchema(RestaurantDTO),
      },
    },
    handler: async (req, res) => {
      const test = await fastify.db.select().from(restaurantsTable).limit(10);

      return res.send({ data: test });
    },
  });
};

export default route;
