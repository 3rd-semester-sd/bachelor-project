import { BasePlugin } from "~/types/BasePlugin";
import { RestaurantMenuItemCRUD } from "~/crud/restaurantMenuItemCRUD";
import { paginationDTO } from "~/dtos/requestDTOs";
import {
  dataResponseDTO,
  paginatedDataListResponseDTO,
} from "~/dtos/responseDTOs";
import { z } from "zod";

export const route: BasePlugin = async (fastify, opts) => {
  const restaurantMenuItemCRUD = new RestaurantMenuItemCRUD(fastify);
  const commonResponses = {
    500: z.object({ error: z.string() }),
  };

  fastify.route({
    method: "GET",
    url: ``,
    schema: {
      tags: restaurantMenuItemCRUD.tags,
      querystring: paginationDTO,
      response: {
        200: paginatedDataListResponseDTO(restaurantMenuItemCRUD.responseDTO),
        ...commonResponses,
      },
    },
    handler: restaurantMenuItemCRUD.handleGetAll.bind(restaurantMenuItemCRUD),
  });

  fastify.route({
    method: "GET",
    url: `/:id`,
    schema: {
      tags: restaurantMenuItemCRUD.tags,
      params: z.object({ id: z.string().uuid() }),
      response: {
        200: dataResponseDTO(restaurantMenuItemCRUD.responseDTO),
        ...commonResponses,
      },
    },
    handler: restaurantMenuItemCRUD.handleGetOne.bind(restaurantMenuItemCRUD),
  });
};

export default route;
