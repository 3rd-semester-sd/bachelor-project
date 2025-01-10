ALTER TABLE "restaurants" DROP CONSTRAINT "restaurants_member_id_restaurant_members_member_id_fk";
--> statement-breakpoint
ALTER TABLE "restaurants" DROP COLUMN "member_id";