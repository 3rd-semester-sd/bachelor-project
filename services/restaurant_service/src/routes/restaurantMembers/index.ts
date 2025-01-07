import { BasePlugin } from "~/types/BasePlugin";
import { RestaurantMemberCRUD } from "~/crud/restaurantMemberCRUD";

export const route: BasePlugin = async (fastify, opts) => {
  const restaurantMembersCRUD = new RestaurantMemberCRUD(fastify);

  // register standard CRUD routes
  restaurantMembersCRUD.registerRoutes();

  // add custom routes
};

export default route;
