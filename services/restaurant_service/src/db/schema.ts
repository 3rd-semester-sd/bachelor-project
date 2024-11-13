import {
  integer,
  pgTable,
  uuid,
  varchar,
  numeric,
  index,
  uniqueIndex,
  pgEnum,
} from "drizzle-orm/pg-core";
import { CuisineType, enumToPgEnum, MenuCategory } from "~/db/enums";

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
export const restaurantsTable = pgTable("restaurant", {
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
  // TODO: price behaves weird
  price: numeric({ precision: 2 }),
  category: menuCategoryPgEnum(),
});

export type User = typeof usersTable.$inferInsert;
export type Restaurant = typeof restaurantsTable.$inferInsert;
export type Menu = typeof menuTable.$inferInsert;
export type MenuItem = typeof menuItemTable.$inferInsert;
