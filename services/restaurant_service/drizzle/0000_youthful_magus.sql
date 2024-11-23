CREATE TYPE "public"."cuisineTypeEnum" AS ENUM('italian', 'japanese', 'mexican', 'indian', 'french');--> statement-breakpoint
CREATE TYPE "public"."menuCategoryEnum" AS ENUM('appetizer', 'main_dish', 'sides', 'desserts');--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "menu_item" (
	"item_id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"menu_id" uuid,
	"item_name" varchar(255) NOT NULL,
	"item_description" varchar(255) NOT NULL,
	"price" numeric(2),
	"category" "menuCategoryEnum"
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "menu" (
	"menu_id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"restaurant_id" uuid,
	"menu_name" varchar(255) NOT NULL,
	"menu_description" varchar(255) NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "restaurant" (
	"restaurant_id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"restaurant_name" varchar(255) NOT NULL,
	"restaurant_address" varchar(255) NOT NULL,
	"restaurant_location" varchar(255) NOT NULL,
	"cuisine_type" "cuisineTypeEnum"
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "users" (
	"user_id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"name" varchar(255) NOT NULL,
	"age" integer NOT NULL,
	"email" varchar(255) NOT NULL,
	CONSTRAINT "users_email_unique" UNIQUE("email")
);
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "menu_item" ADD CONSTRAINT "menu_item_menu_id_menu_menu_id_fk" FOREIGN KEY ("menu_id") REFERENCES "public"."menu"("menu_id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "menu" ADD CONSTRAINT "menu_restaurant_id_restaurant_restaurant_id_fk" FOREIGN KEY ("restaurant_id") REFERENCES "public"."restaurant"("restaurant_id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "name_idx" ON "users" USING btree ("name");--> statement-breakpoint
CREATE UNIQUE INDEX IF NOT EXISTS "email_idx" ON "users" USING btree ("email");