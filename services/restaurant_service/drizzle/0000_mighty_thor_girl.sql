CREATE TYPE "public"."cuisineTypeEnum" AS ENUM('italian', 'japanese', 'mexican', 'indian', 'french');--> statement-breakpoint
CREATE TYPE "public"."menuCategoryEnum" AS ENUM('appetizer', 'main_dish', 'sides', 'desserts');--> statement-breakpoint
CREATE TABLE "menu_items" (
	"item_id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"menu_id" uuid,
	"item_name" varchar(255) NOT NULL,
	"item_description" varchar(255) NOT NULL,
	"price" numeric(2),
	"category" "menuCategoryEnum"
);
--> statement-breakpoint
CREATE TABLE "menus" (
	"menu_id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"restaurant_id" uuid,
	"menu_name" varchar(255) NOT NULL,
	"menu_description" varchar(255) NOT NULL
);
--> statement-breakpoint
CREATE TABLE "restaurant_settings" (
	"restaurant_settings_id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"restaurant_id" uuid NOT NULL,
	"max_seats" integer DEFAULT 30 NOT NULL,
	"opening_hr" integer DEFAULT 10 NOT NULL,
	"closing_hr" integer DEFAULT 22 NOT NULL,
	"open_days" integer[] DEFAULT '{1,1,1,1,1,1,0}' NOT NULL,
	"reservation_time_hr" integer DEFAULT 2 NOT NULL,
	"closing_time_buffer_hr" integer DEFAULT 2 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "restaurants" (
	"restaurant_id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"owner_id" uuid NOT NULL,
	"restaurant_name" varchar(255) NOT NULL,
	"restaurant_address" varchar(255) NOT NULL,
	"restaurant_location" varchar(255) NOT NULL,
	"restaurant_description" varchar(5120) NOT NULL,
	"cuisine_type" "cuisineTypeEnum"
);
--> statement-breakpoint
CREATE TABLE "restaurant_members" (
	"user_id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"name" varchar(255) NOT NULL,
	"email" varchar(255) NOT NULL,
	CONSTRAINT "restaurant_members_email_unique" UNIQUE("email")
);
--> statement-breakpoint
ALTER TABLE "menu_items" ADD CONSTRAINT "menu_items_menu_id_menus_menu_id_fk" FOREIGN KEY ("menu_id") REFERENCES "public"."menus"("menu_id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "menus" ADD CONSTRAINT "menus_restaurant_id_restaurants_restaurant_id_fk" FOREIGN KEY ("restaurant_id") REFERENCES "public"."restaurants"("restaurant_id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "restaurant_settings" ADD CONSTRAINT "restaurant_settings_restaurant_id_restaurants_restaurant_id_fk" FOREIGN KEY ("restaurant_id") REFERENCES "public"."restaurants"("restaurant_id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "restaurants" ADD CONSTRAINT "restaurants_owner_id_restaurant_members_user_id_fk" FOREIGN KEY ("owner_id") REFERENCES "public"."restaurant_members"("user_id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "name_idx" ON "restaurant_members" USING btree ("name");--> statement-breakpoint
CREATE UNIQUE INDEX "email_idx" ON "restaurant_members" USING btree ("email");