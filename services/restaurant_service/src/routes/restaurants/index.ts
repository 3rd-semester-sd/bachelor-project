import { count, eq } from "drizzle-orm";
import { BasePlugin } from "~/types/BasePlugin";
import { restaurantsTable } from "~/db/schema";
import {
  dataResponseDTO,
  paginatedDataListResponseDTO,
} from "~/dtos/response_dtos";
import { restaurantDTO } from "~/dtos/restaurant_dtos";
import { paginationDTO } from "~/dtos/request_dtos";
import { z } from "zod";

export const route: BasePlugin = async (fastify, opts) => {
  fastify.route({
    method: "GET",
    url: "",
    schema: {
      tags: ["Restaurant"],
      querystring: paginationDTO,
      response: {
        200: paginatedDataListResponseDTO(restaurantDTO),
        500: z.object({ error: z.string() }),
      },
    },
    handler: async (req, res) => {
      const { page, page_size: pageSize } = req.query;
      const offset = (page - 1) * pageSize;

      // select paginated data and total count
      try {
        const [data, totalItems] = await Promise.all([
          fastify.db
            .select()
            .from(restaurantsTable)
            .offset(offset)
            .limit(pageSize),
          fastify.db.select({ count: count() }).from(restaurantsTable),
        ]);

        const totalPages = Math.ceil(totalItems[0].count / pageSize);

        return res.status(200).send({
          data: data,
          pagination: {
            total_items: totalItems[0].count,
            total_pages: totalPages,
            current_page: page,
            page_size: pageSize,
          },
        });
      } catch (e) {
        return res.status(500).send({ error: `something went wrong: ${e}` });
      }
    },
  });

  fastify.route({
    method: "GET",
    url: "/:id",
    schema: {
      tags: ["Restaurant"],
      params: z.object({ id: z.string().uuid() }),
      response: {
        200: dataResponseDTO(restaurantDTO),
        500: z.object({ error: z.string() }),
      },
    },
    handler: async (req, res) => {
      const { id } = req.params;

      try {
        const result = await fastify.db
          .select()
          .from(restaurantsTable)
          .where(eq(restaurantsTable.restaurant_id, id));
        return res.status(200).send({ data: result[0] });
      } catch (e) {
        return res.status(500).send({ error: `something went wrong: ${e}` });
      }
    },
  });

  fastify.route({
    method: "POST",
    url: "",
    schema: { tags: ["Restaurant"] },
    handler: async (req, res) => {},
  });
  fastify.route({
    method: "PATCH",
    url: "/:id",
    schema: { tags: ["Restaurant"] },
    handler: async (req, res) => {},
  });

  fastify.route({
    method: "DELETE",
    url: "/:id",
    schema: { tags: ["Restaurant"] },
    handler: async (req, res) => {},
  });
};

export default route;
