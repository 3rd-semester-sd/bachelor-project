import * as schema from "~/db/schema";
import { RestaurantMember, Restaurant, Menu, MenuItem } from "~/db/schema";
import { getDbClient } from "~/db/db";
import { faker } from "@faker-js/faker";
import { CuisineType, MenuCategory } from "../enums";
import "dotenv/config";

// Generate and insert test data

export async function main() {
  const db = await getDbClient(
    process.env.RESTAURANT_DATABASE_URL ||
      "postgresql://restaurant:restaurant@localhost:5432/pg-restaurant-service"
  );

  for (let index = 0; index < 10; index++) {
    const user: RestaurantMember = {
      name: faker.person.fullName(),
      email: faker.internet.email(),
    };

    await db.insert(schema.restaurantMembersTable).values(user);
    console.log("Random user created!");
  }

  // // Insert a test restaurant
  // const restaurant: Restaurant = {
  //   restaurant_name: faker.company.name(),
  //   restaurant_address: faker.location.streetAddress(),
  //   restaurant_location: faker.location.city(),
  //   restaurant_description: faker.word.sample(),
  //   cuisine_type: faker.helpers.arrayElement(Object.values(CuisineType)),
  // };

  // const restaurants: string[] = [];
  // for (let index = 0; index < 10; index++) {
  //   const [restaurantResult] = await db
  //     .insert(schema.restaurantsTable)
  //     .values(restaurant)
  //     .returning({ restaurant_id: schema.restaurantsTable.restaurant_id });
  //   console.log("Test restaurant created:", restaurantResult);
  //   restaurants.push(restaurantResult.restaurant_id);
  // }
  // // Insert a test menu for the restaurant
  // const menus: string[] = [];
  // for (const res of restaurants) {
  //   console.log(res);
  //   const menu: Menu = {
  //     restaurant_id: res,
  //     menu_name: `${restaurant.restaurant_name} Menu`,
  //     menu_description: faker.lorem.sentence(),
  //   };

  //   const [menuResult] = await db
  //     .insert(schema.menusTable)
  //     .values(menu)
  //     .returning({ menu_id: schema.menusTable.menu_id });
  //   console.log("Test menu created:", menuResult);
  //   menus.push(menuResult.menu_id);
  // }

  // // Insert test menu items for the menu
  // for (const menu of menus) {
  //   const menuItems: MenuItem[] = Array.from({ length: 5 }).map(() => ({
  //     menu_id: menu,
  //     item_name: faker.commerce.productName(),
  //     item_description: faker.commerce.productDescription(),
  //     price: faker.number
  //       .float({ min: 5, max: 100, fractionDigits: 2 })
  //       .toString(),
  //     category: faker.helpers.arrayElement(Object.values(MenuCategory)),
  //   }));

  //   console.log(menuItems);
  //   await db.insert(schema.menuItemsTable).values(menuItems);
  //   console.log("Test menu items created!");
  // }
}
// // Execute the seed script
// main().catch((error) => {
//   console.error("Error seeding database:", error);
// });
