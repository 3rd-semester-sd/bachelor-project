import { pgEnum } from "drizzle-orm/pg-core";

export enum CuisineType {
  ITALIAN = "Italian",
  JAPANESE = "Japanese",
  MEXICAN = "Mexican",
  INDIAN = "Indian",
  FRENCH = "French",
}

export function enumToPgEnum<T extends Record<string, any>>(
  myEnum: T
): [T[keyof T], ...T[keyof T][]] {
  return Object.values(myEnum).map((value: any) => `${value}`) as any;
}

export const cuisineTypeEnum = pgEnum(
  "cuisineTypeEnum",
  enumToPgEnum(CuisineType)
);
