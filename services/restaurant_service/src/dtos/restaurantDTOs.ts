import { z } from "zod";
import { CuisineType } from "~/db/enums";

export const restaurantSettingDTO = z.object({
  max_seats: z.number().default(30),
  opening_hr: z.number().default(10),
  closing_hr: z.number().default(22),
  open_days: z.array(z.number()).default([1, 1, 1, 1, 1, 1, 0]),
  reservation_time_hr: z.number().default(2),
  closing_time_buffer_hr: z.number().default(2),
});

export const restaurantResponseDTO = z.object({
  member_id: z.string().uuid(),
  restaurant_id: z.string().uuid(),
  restaurant_name: z.string().max(255),
  restaurant_description: z.string().max(5120),
  restaurant_address: z.string().max(255),
  restaurant_location: z.string().max(255),
  cuisine_type: z.nativeEnum(CuisineType).nullable(),
  restaurant_settings: restaurantSettingDTO,
  // embedding: z.array(z.number()).optional().nullable(),
});

export const restaurantRequestDTO = restaurantResponseDTO.omit({
  restaurant_id: true,
  member_id: true,
  // embedding: true,
});

export type RestaurantSettingDTO = z.infer<typeof restaurantSettingDTO>;
export type RestaurantResponseDTO = z.infer<typeof restaurantResponseDTO>;
