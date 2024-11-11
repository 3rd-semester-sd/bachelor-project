import {
  integer,
  pgTable,
  uuid,
  varchar,
  numeric,
  index,
  uniqueIndex,
  pgEnum
} from "drizzle-orm/pg-core";
// import { cuisineTypePgEnum, menuCategoryPgEnum, CuisineType, MenuCategory } from "~/db/enums.ts";
export enum CuisineType {
  ITALIAN = "italian",
  JAPANESE = "japanese",
  MEXICAN = "mexican",
  INDIAN = "indian",
  FRENCH = "french",
}

export enum MenuCategory {
  APPETIZER = "appetizer",
  MAIN_DISH = "main_dish",
  SIDES = "sides",
  DESSERTS = "desserts",
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
  "menuCategoryEnum",
  enumToPgEnum(MenuCategory)
);

export const usersTable = pgTable(
  "users",
  {
    user_id: uuid().primaryKey().defaultRandom(),
    name: varchar({ length: 255 }).notNull(),
    age: integer().notNull(),
    email: varchar({ length: 255 }).notNull().unique(),
  },
  (t) => [index("name_idx").on(t.name), uniqueIndex("email_idx").on(t.email)]
);
export const restaurantsTable = pgTable("restaurants", {
  restaurant_id: uuid().primaryKey().defaultRandom(),
  restaurant_name: varchar({ length: 255 }).notNull(),
  restaurant_address: varchar({ length: 255 }).notNull(),
  restaurant_location: varchar({ length: 255 }).notNull(),
  cuisine_type: cuisineTypePgEnum(),
});

export const menuTable = pgTable("menu", {
  menu_id: uuid().primaryKey().defaultRandom(),
  restaurant_id: uuid().references(() => restaurantsTable.restaurant_id),
  menu_name: varchar({ length: 255 }).notNull(),
  menu_description: varchar({ length: 255 }).notNull(),
});

export const menuItemTable = pgTable("menu_item", {
  item_id: uuid().primaryKey().defaultRandom(),
  menu_id: uuid().references(() => menuTable.menu_id),
  item_name: varchar({ length: 255 }).notNull(),
  item_description: varchar({ length: 255 }).notNull(),
  price: numeric({ precision: 2 }),
  category: menuCategoryPgEnum(),
});
