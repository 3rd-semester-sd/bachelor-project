import { BasePlugin } from "~/types/BasePlugin";
import { RestaurantCRUD } from "~/crud/restaurantCRUD";

export const route: BasePlugin = async (fastify) => {
  const restaurantCrud = new RestaurantCRUD(fastify);

  restaurantCrud.registerRoutes();
};

export default route;
