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
  RestaurantResponseDTO,
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

      try {
        // search
        const esResult = await fastify.elastic.search<RestaurantResponseDTO>({
          index: "restaurants",
          query: { match_all: {} },
          from: offset,
          size: pageSize,
        });

        //  total count
        const hits = esResult.hits.hits;
        const totalItems = hits.length ?? 0;
        const totalPages = Math.ceil(totalItems / pageSize);

        // documents are in hits[i]._source
        const data = hits.map((hit) => ({
          restaurant_id: hit._id,
          ...hit._source,
        }));
        console.log(data);

        return res.status(200).send({
          data,
          pagination: {
            total_items: totalItems,
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

        // add to index
        await fastify.elastic.index({
          index: "restaurants",
          id: result[0].restaurant_id,
          document: req.body,
        });

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
      const { id } = req.params;
      const updateData = req.body;

      try {
        const result = await fastify.db
          .update(restaurantsTable)
          .set(updateData)
          .where(eq(restaurantsTable.restaurant_id, id))
          .returning();

        if (result.length === 0) {
          return res.status(404).send({ error: "No restaurant found." });
        }

        // update the Elasticsearch document with partial update
        try {
          await fastify.elastic.update({
            index: "restaurants",
            id: id,
            doc: updateData,
          });
        } catch (esError) {
          return res
            .status(500)
            .send({ error: `ES update failed: ${esError}` });
        }
        return res.status(200).send({ data: id });
      } catch (dbError) {
        return res.status(500).send({ error: `DB update failed: ${dbError}` });
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
      const { id } = req.params;

      try {
        const result = await fastify.db
          .delete(restaurantsTable)
          .where(eq(restaurantsTable.restaurant_id, id))
          .returning();

        if (result.length === 0) {
          return res.status(404).send({ error: "No restaurant found." });
        }

        // delete the document in Elasticsearch
        try {
          await fastify.elastic.delete({
            index: "restaurants",
            id: id,
          });
        } catch (esError) {
          return res
            .status(500)
            .send({ error: `ES delete failed: ${esError}` });
        }

        return res.status(200).send({ data: id });
      } catch (dbError) {
        return res.status(500).send({ error: `DB delete failed: ${dbError}` });
      }
    },
  });
};

export default route;
