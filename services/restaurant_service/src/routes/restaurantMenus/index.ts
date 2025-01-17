import { BasePlugin } from "~/types/BasePlugin";

import { RestaurantMenuCRUD } from "~/crud/restaurantMenuCRUD";
import { z } from "zod";
import { paginationDTO } from "~/dtos/requestDTOs";
import { dataResponseDTO, paginatedDataListResponseDTO } from "~/dtos/responseDTOs";

export const route: BasePlugin = async (fastify, opts) => {
  const restaurantMenuCRUD = new RestaurantMenuCRUD(fastify);

  const commonResponses = {
    500: z.object({ error: z.string() }),
  };

  fastify.route({
    method: "GET",
    url: ``,
    schema: {
      tags: restaurantMenuCRUD.tags,
      querystring: paginationDTO,
      response: {
        200: paginatedDataListResponseDTO(restaurantMenuCRUD.responseDTO),
        ...commonResponses,
      },
    },
    handler: restaurantMenuCRUD.handleGetAll.bind(restaurantMenuCRUD),
  });

  fastify.route({
    method: "GET",
    url: `/:id`,
    schema: {
      tags: restaurantMenuCRUD.tags,
      params: z.object({ id: z.string().uuid() }),
      response: {
        200: dataResponseDTO(restaurantMenuCRUD.responseDTO),
        ...commonResponses,
      },
    },
    handler: restaurantMenuCRUD.handleGetOne.bind(restaurantMenuCRUD),
  });
};

export default route;
