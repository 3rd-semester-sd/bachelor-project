import { z } from "zod";
import { CuisineType } from "~/db/enums";

export const restaurantResponseDTO = z.object({
  restaurant_id: z.string().uuid(),
  restaurant_name: z.string().max(255),
  restaurant_description: z.string().max(5120),
  restaurant_address: z.string().max(255),
  restaurant_location: z.string().max(255),
  cuisine_type: z.nativeEnum(CuisineType).nullable(),
  embedding: z.array(z.number()).optional().nullable(),
});

export const restaurantRequestDTO = restaurantResponseDTO.omit({
  restaurant_id: true,
});

export type RestaurantResponseDTO = z.infer<typeof restaurantResponseDTO>;
