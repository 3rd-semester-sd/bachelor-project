import { count } from "drizzle-orm";
import { BasePlugin } from "~/types/BasePlugin";
import { restaurantsTable } from "~/db/schema";
import { paginatedDataListResponseDTO } from "~/dtos/response_dtos";
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
      // calculate the offset
      const offset = (page - 1) * pageSize;

      // select paginated data and total count
      const [data, totalItems] = await Promise.all([
        fastify.db
          .select()
          .from(restaurantsTable)
          .offset(offset)
          .limit(pageSize),
        fastify.db.select({ count: count() }).from(restaurantsTable),
      ]);

      if (data.length < 1) {
        return;
      }

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
    },
  });
};

export default route;
