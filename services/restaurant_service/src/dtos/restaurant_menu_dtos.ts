import { z } from "zod";

export const restaurantMenuDTO = z.object({
  menu_id: z.string().uuid(),
  restaurant_id: z.string().uuid(),
  menu_name: z.string(),
  menu_description: z.string(),
});
export const restaurantMenuRequestDTO = restaurantMenuDTO.omit({
  menu_id: true,
});

export type RestaurantMenu = z.infer<typeof restaurantMenuDTO>;
