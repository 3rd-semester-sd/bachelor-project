import { BasePlugin } from "~/types/BasePlugin";
import { menusTable } from "~/db/schema";
import {
  RestaurantMenu,
  restaurantMenuDTO,
  restaurantMenuRequestDTO,
} from "~/dtos/restaurantMenuDTOs";
import { CRUDBase } from "~/utils/baseCRUD";
import { RestaurantMenuCRUD } from "~/utils/restaurantMenuCRUD";

export const route: BasePlugin = async (fastify, opts) => {
  const restaurantMenuCRUD = new RestaurantMenuCRUD(fastify);

  // register standard CRUD routes
  restaurantMenuCRUD.registerRoutes();

  // add custom routes
};

export default route;
