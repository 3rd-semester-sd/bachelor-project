ALTER TABLE "restaurants" RENAME COLUMN "owner_id" TO "member_id";--> statement-breakpoint
ALTER TABLE "restaurant_members" RENAME COLUMN "user_id" TO "member_id";--> statement-breakpoint
ALTER TABLE "restaurants" DROP CONSTRAINT "restaurants_owner_id_restaurant_members_user_id_fk";
--> statement-breakpoint
ALTER TABLE "restaurants" ADD CONSTRAINT "restaurants_member_id_restaurant_members_member_id_fk" FOREIGN KEY ("member_id") REFERENCES "public"."restaurant_members"("member_id") ON DELETE no action ON UPDATE no action;