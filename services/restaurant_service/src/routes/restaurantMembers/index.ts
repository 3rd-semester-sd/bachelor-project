import { count, eq } from "drizzle-orm";
import { BasePlugin } from "~/types/BasePlugin";
import { restaurantMembersTable } from "~/db/schema";
import {
  restaurantMemberDTO,
  restaurantMemberRequestDTO,
} from "~/dtos/restaurantMemberDTOs";
import { CRUDBase } from "~/utils/baseCRUD";

export const route: BasePlugin = async (fastify, opts) => {
  const restaurantMembersCRUD = new CRUDBase<
    typeof restaurantMembersTable,
    typeof restaurantMemberDTO,
    typeof restaurantMemberRequestDTO
  >(
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
