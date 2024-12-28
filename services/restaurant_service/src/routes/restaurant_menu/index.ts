import { BasePlugin } from "~/types/BasePlugin";
import { menusTable } from "~/db/schema";
import {
  RestaurantMenu,
  restaurantMenuDTO,
  restaurantMenuRequestDTO,
} from "~/dtos/restaurant_menu_dtos";
import { CRUDBase } from "~/utils/baseCRUD";

export const route: BasePlugin = async (fastify, opts) => {
  const restaurantMembersCRUD = new CRUDBase<RestaurantMenu>(
    fastify,
    menusTable,
    "restaurant_menu",
    "menu_id",
    restaurantMenuDTO,
    restaurantMenuRequestDTO,
    ["Restaurant Menu"]
  );

  // register standard CRUD routes
  restaurantMembersCRUD.registerRoutes();

  // add custom routes
};

export default route;
