import { BasePlugin } from "~/types/BasePlugin";

import { RestaurantMenuCRUD } from "~/crud/restaurantMenuCRUD";

export const route: BasePlugin = async (fastify, opts) => {
  const restaurantMenuCRUD = new RestaurantMenuCRUD(fastify);

  // register standard CRUD routes
  restaurantMenuCRUD.registerRoutes();
  
};

export default route;
