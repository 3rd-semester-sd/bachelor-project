import 'dotenv/config';
import { eq } from 'drizzle-orm';
import * as schema from "../../db/schema.js"
import { db } from "~/db/index.js";



async function main() {
    const user: typeof schema.usersTable.$inferInsert = {
        name: 'John',
        age: 30,
        email: 'john@example.com',
    };

    await db.insert(schema.usersTable).values(user);
    console.log('New user created!')

    const users = await db.select().from(schema.usersTable);
    console.log('Getting all users from the database: ', users)
    /*
    const users: {
      id: number;
      name: string;
      age: number;
      email: string;
    }[]
    */

    await db
        .update(schema.usersTable)
        .set({
            age: 31,
        })
        .where(eq(schema.usersTable.email, user.email));
    console.log('User info updated!')

    // await db.delete(schema.usersTable).where(eq(schema.usersTable.email, user.email));
    // console.log('User deleted!')
}

main();
