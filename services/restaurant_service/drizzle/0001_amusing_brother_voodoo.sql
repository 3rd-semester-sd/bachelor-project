ALTER TABLE "public"."menu_item" ALTER COLUMN "category" SET DATA TYPE text;--> statement-breakpoint
DROP TYPE "public"."menuCategoryEnum";--> statement-breakpoint
CREATE TYPE "public"."menuCategoryEnum" AS ENUM('Appetizer', 'Main Dish', 'Sides', 'Desserts');--> statement-breakpoint
ALTER TABLE "public"."menu_item" ALTER COLUMN "category" SET DATA TYPE "public"."menuCategoryEnum" USING "category"::"public"."menuCategoryEnum";