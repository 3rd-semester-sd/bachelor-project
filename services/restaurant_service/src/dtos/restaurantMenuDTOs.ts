import { z } from "zod";
import { restaurantMenuItemRequestDTO } from "./restaurantMenuItemDTOs";

export const restaurantMenuDTO = z.object({
  menu_id: z.string().uuid(),
  restaurant_id: z.string().uuid(),
  menu_name: z.string(),
  menu_description: z.string(),
  menu_items: z.array(restaurantMenuItemRequestDTO).nullable().default([]),
});
export const restaurantMenuRequestDTO = restaurantMenuDTO.omit({
  menu_id: true,
  menu_items: true,
});

export type RestaurantMenu = z.infer<typeof restaurantMenuDTO>;
