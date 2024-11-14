import { z, ZodSchema, ZodTypeAny } from "zod";
import camelcaseKeys from "camelcase-keys";
import { CuisineType } from "~/db/enums";

function isObject(data: unknown): data is Record<string, unknown> {
  return typeof data === "object" && data !== null;
}

function camelCaseTransformer<T extends ZodTypeAny>(schema: T): ZodSchema {
  return z.preprocess((data) => {
    if (isObject(data)) {
      return camelcaseKeys(data, { deep: true });
    }
    return data;
  }, schema);
}
export const UserSchema = z.object({
  userId: z.string().uuid(),
  name: z.string().max(255),
  age: z.number().int(),
  email: z.string().email(),
});

export const RestaurantDTO = camelCaseTransformer(
  z.object({
    restaurantId: z.string().uuid(),
    restaurantName: z.string().max(255),
    restaurantAddress: z.string().max(255),
    restaurantLocation: z.string().max(255),
    cuisineType: z.nativeEnum(CuisineType).nullable(),
  })
);
