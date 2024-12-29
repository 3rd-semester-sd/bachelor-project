CREATE TYPE "public"."restaurantStatusEnum" AS ENUM('active', 'pending');--> statement-breakpoint
ALTER TABLE "restaurants" ADD COLUMN "restaurant_status" "restaurantStatusEnum" DEFAULT 'pending';