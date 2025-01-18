import { BasePlugin } from "~/types/BasePlugin";
import { RestaurantCRUD } from "~/crud/restaurantCRUD";
import { z } from "zod";
import { PostgresService } from "~/services/pgService";
import { ElasticsearchService } from "~/services/elasticsearchService";
import { restaurantsTable } from "~/db/schema";
import { restaurantResponseDTO } from "~/dtos/restaurantDTOs";
import { paginationDTO } from "~/dtos/requestDTOs";
import { paginatedDataListResponseDTO } from "~/dtos/responseDTOs";

export const route: BasePlugin = async (fastify) => {
  // Initialize services with fastify instance
  const pgService = new PostgresService(
    fastify,
    restaurantsTable,
    "restaurant_id"
  );
  const esService = new ElasticsearchService<typeof restaurantResponseDTO>(
    fastify,
    "restaurants"
  );
  const restaurantCrud = new RestaurantCRUD(fastify, pgService, esService);

  restaurantCrud.registerRoutes();

  fastify.route({
    method: "POST",
    url: "/search",
    schema: {
      tags: ["Restaurant"],
      querystring: paginationDTO,
      body: z.object({ input: z.string() }),
      response: {
        200: paginatedDataListResponseDTO(restaurantResponseDTO),
      },
    },
    handler: async (req, res) => {
      const test = req.body;
      const esResult = await esService.search({
        multi_match: {
          query: req.body.input,
          fields: ["restaurant_name", "restaurant_description"],
        },
      });
      return restaurantCrud.formatPaginatedResponse(
        esResult,
        req.query.page,
        req.query.page_size
      );
    },
  });
};

export default route;
