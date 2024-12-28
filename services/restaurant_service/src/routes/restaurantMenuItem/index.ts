import { BasePlugin } from "~/types/BasePlugin";
import { RestaurantMenuItemCRUD } from "~/utils/restaurantMenuItemCRUD";

export const route: BasePlugin = async (fastify, opts) => {
  const restaurantMenuItemCRUD = new RestaurantMenuItemCRUD(fastify);

  // register standard CRUD routes
  restaurantMenuItemCRUD.registerRoutes();

  // add custom routes
};

export default route;
