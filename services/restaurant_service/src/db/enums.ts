import { pgEnum } from "drizzle-orm/pg-core";

export enum CuisineType {
  ITALIAN = "italian",
  JAPANESE = "japanese",
  MEXICAN = "mexican",
  INDIAN = "indian",
  FRENCH = "french",
}

export enum MenuCategory {
  APPETIZER = "Appetizer",
  MAIN_DISH = "Main Dish",
  SIDES = "Sides",
  DESSERTS = "Desserts",
}

export function enumToPgEnum<T extends Record<string, any>>(
  myEnum: T
): [T[keyof T], ...T[keyof T][]] {
  return Object.values(myEnum).map((value: any) => `${value}`) as any;
}

export const cuisineTypePgEnum = pgEnum(
  "cuisineTypeEnum",
  enumToPgEnum(CuisineType)
);

export const menuCategoryPgEnum = pgEnum(
  "cuisineTypeEnum",
  enumToPgEnum(CuisineType)
);
