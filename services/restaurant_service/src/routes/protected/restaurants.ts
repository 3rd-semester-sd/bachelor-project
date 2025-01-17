// src/routes/restaurants.ts
import { FastifyInstance, FastifyReply, FastifyRequest } from "fastify";
import { RestaurantCRUD } from "~/crud/restaurantCRUD";
import { PostgresService } from "~/services/pgService";
import { ElasticsearchService } from "~/services/elasticsearchService";
import { restaurantsTable, restaurantSettingsTable } from "~/db/schema";
import { restaurantResponseDTO } from "~/dtos/restaurantDTOs";
import { z } from "zod";
import { defaultResponseDTO } from "~/dtos/responseDTOs";

export default async function (fastify: FastifyInstance, opts: any) {
  // Initialize services
  const pgService = new PostgresService<typeof restaurantsTable>(
    fastify,
    restaurantsTable,
    "restaurant_id"
  );
  const esService = new ElasticsearchService<typeof restaurantResponseDTO>(
    fastify,
    "restaurants"
  );
  // Instantiate RestaurantCRUD
  const restaurantCRUD = new RestaurantCRUD(fastify, pgService, esService);

  const prefix = "/restaurants";
  const commonResponses = {
    500: z.object({ error: z.string() }),
  };

  fastify.route({
    method: "POST",
    url: `${prefix}`,
    schema: {
      tags: restaurantCRUD.tags,
      body: restaurantCRUD.requestDTO,
      response: {
        200: defaultResponseDTO,
        ...commonResponses,
      },
      security: [{ bearerAuth: [] }],
    },
    handler: restaurantCRUD.handleCreate.bind(restaurantCRUD),
  });

  fastify.route({
    method: "PATCH",
    url: `${prefix}/:id`,
    schema: {
      tags: restaurantCRUD.tags,
      params: z.object({ id: z.string().uuid() }),
      body: restaurantCRUD.requestDTO.partial(),
      response: {
        200: defaultResponseDTO,
        ...commonResponses,
      },
      security: [{ bearerAuth: [] }],
    },
    handler: restaurantCRUD.handleUpdate.bind(restaurantCRUD),
  });

  fastify.route({
    method: "DELETE",
    url: `${prefix}/:id`,
    schema: {
      tags: restaurantCRUD.tags,
      params: z.object({ id: z.string().uuid() }),
      response: {
        200: defaultResponseDTO,
        ...commonResponses,
      },
      security: [{ bearerAuth: [] }],
    },
    handler: restaurantCRUD.handleDelete.bind(restaurantCRUD),
  });
}
