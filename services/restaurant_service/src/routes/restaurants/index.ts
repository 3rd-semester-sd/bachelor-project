import { count } from "drizzle-orm";
import { BasePlugin } from "~/types/BasePlugin";
import { restaurantsTable } from "~/db/schema";
import { PaginatedDataListResponseSchema } from "~/dtos/response_dtos";
import { RestaurantDTO } from "~/dtos/restaurant_dtos";
import { PaginationSchema } from "~/dtos/request_dtos";

export const route: BasePlugin = async (fastify, opts) => {
  fastify.route({
    method: "GET",
    url: "",
    schema: {
      tags: ["Restaurant"],
      querystring: PaginationSchema,
      response: {
        200: PaginatedDataListResponseSchema(RestaurantDTO),
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

      const totalPages = Math.ceil(totalItems[0].count / pageSize);

      return res.send({
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
