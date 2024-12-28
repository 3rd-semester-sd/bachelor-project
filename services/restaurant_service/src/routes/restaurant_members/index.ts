import { count, eq } from "drizzle-orm";
import { BasePlugin } from "~/types/BasePlugin";
import { restaurantMembersTable } from "~/db/schema";
import {
  RestaurantMember,
  restaurantMemberDTO,
  restaurantMemberRequestDTO,
} from "~/dtos/restaurant_member_dtos";
import { paginationDTO } from "~/dtos/request_dtos";
import { z } from "zod";
import { CRUDBase } from "~/utils/baseCRUD";

export const route: BasePlugin = async (fastify, opts) => {
  const restaurantMembersCRUD = new CRUDBase<RestaurantMember>(
    fastify,
    restaurantMembersTable,
    "restaurant_members",
    "member_id",
    restaurantMemberDTO,
    restaurantMemberRequestDTO,
    ["Restaurant member"]
  );

  // register standard CRUD routes
  restaurantMembersCRUD.registerRoutes();

  // add custom routes
};

export default route;
