import { z } from "zod";
import { CuisineType } from "~/db/enums";

// User schema
export const UserSchema = z.object({
  user_id: z.string().uuid(),
  name: z.string().max(255),
  age: z.number().int(),
  email: z.string().email(),
});

// Restaurant schema
export const RestaurantDTO = z.object({
  restaurant_name: z.string().max(255),
  restaurant_address: z.string().max(255),
  restaurant_location: z.string().max(255),
  cuisine_type: z.nativeEnum(CuisineType).nullable(),
});
