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
ALTER TABLE "restaurant_settings" ADD CONSTRAINT "restaurant_settings_restaurant_id_restaurant_restaurant_id_fk" FOREIGN KEY ("restaurant_id") REFERENCES "public"."restaurant"("restaurant_id") ON DELETE no action ON UPDATE no action;