import { BasePlugin } from "~/types/BasePlugin";
import { RestaurantMemberCRUD } from "~/crud/restaurantMemberCRUD";
import {
  dataResponseDTO,
  paginatedDataListResponseDTO,
} from "~/dtos/responseDTOs";
import { paginationDTO } from "~/dtos/requestDTOs";
import { z } from "zod";

export const route: BasePlugin = async (fastify, opts) => {
  const restaurantMembersCRUD = new RestaurantMemberCRUD(fastify);

  const commonResponses = {
    500: z.object({ error: z.string() }),
  };

  fastify.route({
    method: "GET",
    url: ``,
    schema: {
      tags: restaurantMembersCRUD.tags,
      querystring: paginationDTO,
      response: {
        200: paginatedDataListResponseDTO(restaurantMembersCRUD.responseDTO),
        ...commonResponses,
      },
    },
    handler: restaurantMembersCRUD.handleGetAll.bind(restaurantMembersCRUD),
  });

  fastify.route({
    method: "GET",
    url: `/:id`,
    schema: {
      tags: restaurantMembersCRUD.tags,
      params: z.object({ id: z.string().uuid() }),
      response: {
        200: dataResponseDTO(restaurantMembersCRUD.responseDTO),
        ...commonResponses,
      },
    },
    handler: restaurantMembersCRUD.handleGetOne.bind(restaurantMembersCRUD),
  });
};

export default route;
