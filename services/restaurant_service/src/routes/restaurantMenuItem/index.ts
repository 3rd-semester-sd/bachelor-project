import { BasePlugin } from "~/types/BasePlugin";
import { menusTable } from "~/db/schema";
import {
  RestaurantMenu,
  restaurantMenuDTO,
  restaurantMenuRequestDTO,
} from "~/dtos/restaurantMenuDTOs";
import { CRUDBase } from "~/utils/baseCRUD";
import { RestaurantMenuItem } from "~/dtos/restaurantMenuItemDTOs";

export const route: BasePlugin = async (fastify, opts) => {
  const restaurantMembersCRUD = new CRUDBase<RestaurantMenuItem>(
    fastify,
    menusTable,
    "restaurant_menu",
    "menu_id",
    restaurantMenuDTO,
    restaurantMenuRequestDTO,
    ["Restaurant Menu Item"]
  );

  // register standard CRUD routes
  restaurantMembersCRUD.registerRoutes();

  // add custom routes
};

export default route;
