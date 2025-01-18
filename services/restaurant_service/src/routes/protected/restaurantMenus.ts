import { BasePlugin } from "~/types/BasePlugin";
import { defaultResponseDTO } from "~/dtos/responseDTOs";
import { z } from "zod";
import { RestaurantMenuCRUD } from "~/crud/restaurantMenuCRUD";

export const route: BasePlugin = async (fastify, opts) => {
  const restaurantMembersCRUD = new RestaurantMenuCRUD(fastify);

  const prefix = "/restaurant-menus";
  const commonResponses = {
    500: z.object({ error: z.string() }),
  };

  fastify.route({
    method: "POST",
    url: `${prefix}`,
    schema: {
      tags: restaurantMembersCRUD.tags,
      body: restaurantMembersCRUD.requestDTO,
      response: {
        200: defaultResponseDTO,
        ...commonResponses,
      },
      security: [{ bearerAuth: [] }],
    },
    handler: restaurantMembersCRUD.handleCreate.bind(restaurantMembersCRUD),
  });

  fastify.route({
    method: "PATCH",
    url: `${prefix}/:id`,
    schema: {
      tags: restaurantMembersCRUD.tags,
      params: z.object({ id: z.string().uuid() }),
      body: restaurantMembersCRUD.requestDTO.partial(),
      response: {
        200: defaultResponseDTO,
        ...commonResponses,
      },
      security: [{ bearerAuth: [] }],
    },
    handler: restaurantMembersCRUD.handleUpdate.bind(restaurantMembersCRUD),
  });

  fastify.route({
    method: "DELETE",
    url: `${prefix}/:id`,
    schema: {
      tags: restaurantMembersCRUD.tags,
      params: z.object({ id: z.string().uuid() }),
      response: {
        200: defaultResponseDTO,
        ...commonResponses,
      },
      security: [{ bearerAuth: [] }],
    },
    handler: restaurantMembersCRUD.handleDelete.bind(restaurantMembersCRUD),
  });
};

export default route;
