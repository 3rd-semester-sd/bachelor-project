import { z } from "zod";
import { MenuCategory } from "~/db/enums";

export const restaurantMenuItemDTO = z.object({
  item_id: z.string().uuid(),
  menu_id: z.string().uuid(),
  item_name: z.string(),
  item_description: z.string(),
  price: z.number(),
  category: z.nativeEnum(MenuCategory),
});

export const restaurantMenuItemRequestDTO = restaurantMenuItemDTO.omit({
  item_id: true,
});

export type RestaurantMenuItem = z.infer<typeof restaurantMenuItemRequestDTO>;
