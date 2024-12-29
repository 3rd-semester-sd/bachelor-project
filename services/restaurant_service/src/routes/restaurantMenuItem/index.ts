import { BasePlugin } from "~/types/BasePlugin";
import { RestaurantMenuItemCRUD } from "~/crud/restaurantMenuItemCRUD";

export const route: BasePlugin = async (fastify, opts) => {
  const restaurantMenuItemCRUD = new RestaurantMenuItemCRUD(fastify);

  // register standard CRUD routes
  restaurantMenuItemCRUD.registerRoutes();
};

export default route;
