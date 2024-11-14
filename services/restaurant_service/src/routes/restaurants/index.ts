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
      const { page, pageSize } = req.query;

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

      const transformedData = data.map((item) => RestaurantDTO.parse(item));

      return res.send({
        data: transformedData,
        pagination: {
          totalItems: totalItems[0].count,
          totalPages,
          currentPage: page,
          pageSize,
        },
      });
    },
  });
};

export default route;
