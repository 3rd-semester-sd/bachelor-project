// src/routes/restaurants.ts
import { FastifyInstance, FastifyReply, FastifyRequest } from "fastify";
import { RestaurantCRUD } from "~/crud/restaurantCRUD";
import { PostgresService } from "~/services/pgService";
import { ElasticsearchService } from "~/services/elasticsearchService";
import { restaurantsTable, restaurantSettingsTable } from "~/db/schema";
import {
  restaurantRequestDTO,
  restaurantResponseDTO,
} from "~/dtos/restaurantDTOs";
import { z } from "zod";
import {
  PaginationDTO,
  paginationDTO,
  SearchBodyDTO,
} from "~/dtos/requestDTOs";
import {
  dataListResponseDTO,
  dataResponseDTO,
  defaultResponseDTO,
  paginatedDataListResponseDTO,
} from "~/dtos/responseDTOs";

interface RouteParams {
  restaurant_id: string;
  user_id: string;
}

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

  const commonResponses = {
    500: z.object({ error: z.string() }),
  };

  fastify.route({
    method: "GET",
    url: ``,
    schema: {
      tags: restaurantCRUD.tags,
      querystring: paginationDTO,
      response: {
        200: paginatedDataListResponseDTO(restaurantCRUD.responseDTO),
        ...commonResponses,
      },
    },
    handler: restaurantCRUD.handleGetAll.bind(restaurantCRUD),
  });

  fastify.route({
    method: "GET",
    url: `/:id`,
    schema: {
      tags: restaurantCRUD.tags,
      params: z.object({ id: z.string().uuid() }),
      response: {
        200: dataResponseDTO(restaurantCRUD.responseDTO),
        ...commonResponses,
      },
    },
    handler: restaurantCRUD.handleGetOne.bind(restaurantCRUD),
  });

  fastify.route({
    method: "GET",
    url: "/:restaurant_id/members/:user_id",
    schema: {
      tags: restaurantCRUD.tags,
      params: z.object({
        restaurant_id: z.string().uuid(),
        user_id: z.string().uuid(),
      }),
      response: {
        200: dataListResponseDTO(restaurantCRUD.responseDTO),
        ...commonResponses,
      },
    },
    handler: async (
      req: FastifyRequest<{ Params: RouteParams }>,
      reply: FastifyReply
    ) => {
      const { restaurant_id, user_id } = req.params;

      try {
        const esResult = await fastify.elastic.search({
          index: "restaurants",
          body: {
            query: {
              bool: {
                must: [
                  {
                    match: {
                      "restaurant_id.keyword": restaurant_id,
                    },
                  },
                  {
                    match: {
                      "member_id.keyword": user_id,
                    },
                  },
                ],
              },
            },
            _source: true,
          },
        });

        if (esResult.hits.hits.length === 0) {
          return reply
            .status(404)
            .send({ error: "Restaurant not found for this member." });
        }

        const restaurants = esResult.hits.hits.map((hit: any) => ({
          restaurant_id: hit._id,
          ...hit._source,
        }));

        console.log(restaurants);

        return reply.status(200).send({
          data: restaurants,
        });
      } catch (error) {
        req.log.error({
          err: error,
          restaurant_id,
          user_id,
          msg: "Failed to fetch restaurant data",
        });

        return reply.status(500).send({
          error: "Internal Server Error",
        });
      }
    },
  });

  fastify.route({
    method: "POST",
    url: "/search",
    schema: {
      tags: restaurantCRUD.tags,
      querystring: paginationDTO,
      body: z.object({ input: z.string() }),
      response: {
        200: paginatedDataListResponseDTO(restaurantResponseDTO),
      },
    },
    handler: async (
      req: FastifyRequest<{
        Body: SearchBodyDTO;
        Querystring: PaginationDTO;
      }>,
      res
    ) => {
      const esResult = await esService.search({
        multi_match: {
          query: req.body.input,
          fields: ["restaurant_name", "restaurant_description"],
        },
      });
      return restaurantCRUD.formatPaginatedResponse(
        esResult,
        req.query.page,
        req.query.page_size
      );
    },
  });
}
