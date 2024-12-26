import {
  integer,
  pgTable,
  uuid,
  varchar,
  numeric,
  index,
  uniqueIndex,
  pgEnum,
  PgArray,
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
  restaurant_description: varchar({ length: 5120 }).notNull(),
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

export const restaurantSettingsTable = pgTable("restaurant_settings", {
  restaurant_settings_id: uuid("restaurant_settings_id")
    .primaryKey()
    .defaultRandom(),

  // Foreign key to the main restaurant table
  restaurant_id: uuid("restaurant_id")
    .notNull()
    .references(() => restaurantsTable.restaurant_id),

  max_seats: integer("max_seats").notNull().default(30),
  opening_hr: integer("opening_hr").notNull().default(10),
  closing_hr: integer("closing_hr").notNull().default(22),

  open_days: integer("open_days")
    .array()
    .notNull()
    .default([1, 1, 1, 1, 1, 1, 0]),

  reservation_time_hr: integer("reservation_time_hr").notNull().default(2),
  closing_time_buffer_hr: integer("closing_time_buffer_hr")
    .notNull()
    .default(2),
});

export type User = typeof usersTable.$inferInsert;
export type Restaurant = typeof restaurantsTable.$inferInsert;
export type RestaurantSetting = typeof restaurantSettingsTable.$inferInsert;
export type Menu = typeof menuTable.$inferInsert;
export type MenuItem = typeof menuItemTable.$inferInsert;
