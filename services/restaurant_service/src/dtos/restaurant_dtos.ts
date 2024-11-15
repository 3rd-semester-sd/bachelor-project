import { z } from "zod";
import { CuisineType } from "~/db/enums";

export const restaurantDTO = z.object({
  restaurant_id: z.string().uuid(),
  restaurant_name: z.string().max(255),
  restaurant_address: z.string().max(255),
  restaurant_location: z.string().max(255),
  cuisine_type: z.nativeEnum(CuisineType).nullable(),
});

export type RestaurantDTO = z.infer<typeof restaurantDTO>;
