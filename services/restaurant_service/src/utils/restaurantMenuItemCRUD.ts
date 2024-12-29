// restaurantMenuItemCRUD.ts
import { FastifyInstance, FastifyRequest, FastifyReply } from "fastify";
import { menuItemsTable } from "~/db/schema";
import { CRUDBase } from "./baseCRUD";
import {
  restaurantMenuItemDTO,
  restaurantMenuItemRequestDTO,
} from "~/dtos/restaurantMenuItemDTOs";
import { eq } from "drizzle-orm";
import { z } from "zod";

export class RestaurantMenuItemCRUD extends CRUDBase<
  typeof menuItemsTable,
  typeof restaurantMenuItemRequestDTO,
  typeof restaurantMenuItemDTO
> {
  constructor(fastify: FastifyInstance) {
    super(
      fastify,
      menuItemsTable,
      "restaurant_menu_items",
      "item_id",
      restaurantMenuItemRequestDTO,
      restaurantMenuItemDTO,
      ["Restaurant Menu Item"]
    );
  }

  /**
   * Hook runs *after* base class insert. Appends the item to menu_items array in restaurant_menu.
   */
  protected async onAfterCreate(
    insertedId: string,
    insertedData: Partial<(typeof menuItemsTable)["$inferInsert"]>,
    req: FastifyRequest<{ Body: z.infer<typeof restaurantMenuItemRequestDTO> }>
  ): Promise<void> {
    const { elastic } = this.fastify;
    const menuId = req.body.menu_id;

    if (!menuId) return;

    await elastic.update({
      index: "restaurant_menu",
      id: menuId,
      script: {
        lang: "painless",
        source: `
          if (ctx._source.menu_items == null) {
            ctx._source.menu_items = [params.newItem];
          } else {
            ctx._source.menu_items.add(params.newItem);
          }
        `,
        params: { newItem: { item_id: insertedId, ...req.body } },
      },
      upsert: {
        menu_items: [req.body], // array of one object
      },
    });
  }

  /**
   * Hook runs *after* base class update. We find the item in menu_items array and update it.
   */
  protected async onAfterUpdate(
    updatedId: string,
    updatedData: any,
    req: FastifyRequest
  ): Promise<void> {
    const { elastic } = this.fastify;

    const menuId = updatedData[0].menu_id;
    if (!menuId) return;

    // script that loops the items to find the one with item_id === updatedId

    // script that loops the items to find the one with item_id === updatedId
    await elastic.update({
      index: "restaurant_menu",
      id: menuId,
      script: {
        lang: "painless",
        source: `
          if (ctx._source.menu_items != null) {
            for (int i = 0; i < ctx._source.menu_items.size(); i++) {
              if (ctx._source.menu_items[i].item_id == params.updatedId) {
                // Overwrite the old item with the new fields
                ctx._source.menu_items[i] = params.newItem;
              }
            }
          }
        `,
        params: {
          updatedId,
          newItem: updatedData[0],
        },
      },
    });
  }

  /**
   * Hook runs *after* base class delete. Remove the item from menu_items array in restaurant_menu.
   */
  protected async onAfterDelete(deletedId: string): Promise<void> {
    const { fastify } = this;

    // if table has "menu_id" as a foreign key, fetch it from PG:
    const record = await fastify.db
      .select()
      .from(menuItemsTable)
      .where(eq(menuItemsTable.item_id, deletedId))
      .then((rows) => rows[0]);

    const menuId = record.menu_id;

    if (!menuId) return;

    await fastify.elastic.update({
      index: "restaurant_menu",
      id: menuId,
      script: {
        lang: "painless",
        source: `
          if (ctx._source.menu_items != null) {
            ctx._source.menu_items.removeIf(item -> item.item_id == params.deletedId);
          }
        `,
        params: { deletedId },
      },
    });
  }
}
