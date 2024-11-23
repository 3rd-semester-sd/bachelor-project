import { count, eq } from "drizzle-orm";
import { BasePlugin } from "~/types/BasePlugin";
import { restaurantsTable } from "~/db/schema";
import {
  dataResponseDTO,
  defaultResponseDTO,
  paginatedDataListResponseDTO,
} from "~/dtos/response_dtos";
import {
  restaurantRequestDTO,
  restaurantResponseDTO,
} from "~/dtos/restaurant_dtos";
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
        200: paginatedDataListResponseDTO(restaurantResponseDTO),
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
        200: dataResponseDTO(restaurantResponseDTO),
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

        if (result.length === 0) {
          res.status(404).send({ error: "No restaurant found." });
        }
        return res.status(200).send({ data: result[0] });
      } catch (e) {
        return res.status(500).send({ error: `something went wrong: ${e}` });
      }
    },
  });

  fastify.route({
    method: "POST",
    url: "",
    schema: {
      tags: ["Restaurant"],
      body: restaurantRequestDTO,
      response: {
        200: defaultResponseDTO,
        500: z.object({ error: z.string() }),
      },
    },
    handler: async (req, res) => {
      try {
        const result = await fastify.db
          .insert(restaurantsTable)
          .values(req.body)
          .returning({ restaurant_id: restaurantsTable.restaurant_id });

        return res.status(200).send({ data: result[0].restaurant_id });
      } catch (e) {
        return res.status(500).send({ error: `something went wrong: ${e}` });
      }
    },
  });

  fastify.route({
    method: "PATCH",
    url: "/:id",
    schema: {
      tags: ["Restaurant"],
      params: z.object({ id: z.string().uuid() }),
      body: restaurantRequestDTO.partial(),
      response: {
        200: defaultResponseDTO,
        404: z.object({ error: z.string() }),
        500: z.object({ error: z.string() }),
      },
    },
    handler: async (req, res) => {
      try {
        const result = await fastify.db
          .update(restaurantsTable)
          .set(req.body)
          .where(eq(restaurantsTable.restaurant_id, req.params.id))
          .returning();

        if (result.length === 0) {
          res.status(404).send({ error: "No restaurant found." });
        }
        return res.status(200).send({ data: req.params.id });
      } catch (e) {
        return res.status(500).send({ error: `something went wrong: ${e}` });
      }
    },
  });

  fastify.route({
    method: "DELETE",
    url: "/:id",
    schema: {
      tags: ["Restaurant"],
      params: z.object({ id: z.string().uuid() }),
      response: {
        200: defaultResponseDTO,
        404: z.object({ error: z.string() }),
        500: z.object({ error: z.string() }),
      },
    },
    handler: async (req, res) => {
      try {
        const result = await fastify.db
          .delete(restaurantsTable)
          .where(eq(restaurantsTable.restaurant_id, req.params.id))
          .returning();

        if (result.length === 0) {
          res.status(404).send({ error: "No restaurant found." });
        }
        return res.status(200).send({ data: req.params.id });
      } catch (e) {
        return res.status(500).send({ error: `something went wrong: ${e}` });
      }
    },
  });
};

export default route;
