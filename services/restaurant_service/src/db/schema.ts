import { integer, pgEnum, pgTable, uuid, varchar } from "drizzle-orm/pg-core";

export const usersTable = pgTable("users", {
  id: uuid("uuid4").primaryKey().defaultRandom(),
  name: varchar({ length: 255 }).notNull(),
  age: integer().notNull(),
  email: varchar({ length: 255 }).notNull().unique(),
});

export const restaurantsTable = pgTable("restaurants", {
  id: uuid("uuid4").primaryKey().defaultRandom(),
  name: varchar({ length: 255 }).notNull(),
  address: varchar({ length: 255 }).notNull(),
  location: varchar({ length: 255 }).notNull(),
  cuisine_type: roleEnum,
});

export enum Role {
  APPLICANT = "applicant",
  TRAINER = "trainer",
  ADMIN = "admin",
}

export function enumToPgEnum<T extends Record<string, any>>(
  myEnum: T
): [T[keyof T], ...T[keyof T][]] {
  return Object.values(myEnum).map((value: any) => `${value}`) as any;
}

export const roleEnum = pgEnum("role", enumToPgEnum(Role));
