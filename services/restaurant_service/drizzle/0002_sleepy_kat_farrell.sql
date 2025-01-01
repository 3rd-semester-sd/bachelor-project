ALTER TABLE "menu_items" DROP CONSTRAINT "menu_items_menu_id_menus_menu_id_fk";
--> statement-breakpoint
ALTER TABLE "menus" DROP CONSTRAINT "menus_restaurant_id_restaurants_restaurant_id_fk";
--> statement-breakpoint
ALTER TABLE "restaurant_settings" DROP CONSTRAINT "restaurant_settings_restaurant_id_restaurants_restaurant_id_fk";
--> statement-breakpoint
ALTER TABLE "restaurants" DROP CONSTRAINT "restaurants_member_id_restaurant_members_member_id_fk";
--> statement-breakpoint
ALTER TABLE "menu_items" ADD CONSTRAINT "menu_items_menu_id_menus_menu_id_fk" FOREIGN KEY ("menu_id") REFERENCES "public"."menus"("menu_id") ON DELETE cascade ON UPDATE cascade;--> statement-breakpoint
ALTER TABLE "menus" ADD CONSTRAINT "menus_restaurant_id_restaurants_restaurant_id_fk" FOREIGN KEY ("restaurant_id") REFERENCES "public"."restaurants"("restaurant_id") ON DELETE cascade ON UPDATE cascade;--> statement-breakpoint
ALTER TABLE "restaurant_settings" ADD CONSTRAINT "restaurant_settings_restaurant_id_restaurants_restaurant_id_fk" FOREIGN KEY ("restaurant_id") REFERENCES "public"."restaurants"("restaurant_id") ON DELETE cascade ON UPDATE cascade;--> statement-breakpoint
ALTER TABLE "restaurants" ADD CONSTRAINT "restaurants_member_id_restaurant_members_member_id_fk" FOREIGN KEY ("member_id") REFERENCES "public"."restaurant_members"("member_id") ON DELETE cascade ON UPDATE cascade;