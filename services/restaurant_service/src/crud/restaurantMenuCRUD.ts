// restaurantMenuItemCRUD.ts
import { FastifyInstance } from "fastify";
import { menusTable } from "~/db/schema";
import { CRUDBase } from "./baseCRUD";
import {
  restaurantMenuDTO,
  restaurantMenuRequestDTO,
} from "~/dtos/restaurantMenuDTOs";
import { PostgresService } from "~/services/pgService";
import { ElasticsearchService } from "~/services/elasticsearchService";

export class RestaurantMenuCRUD extends CRUDBase<
  typeof menusTable,
  typeof restaurantMenuRequestDTO,
  typeof restaurantMenuDTO
> {
  constructor(fastify: FastifyInstance) {
    const pgService = new PostgresService(fastify, menusTable, "menu_id");
    const esService = new ElasticsearchService<typeof restaurantMenuDTO>(
      fastify,
      "restaurant_menu"
    );
    super(
      fastify,
      pgService,
      esService,
      "menu_id",
      restaurantMenuRequestDTO,
      restaurantMenuDTO,
      ["Restaurant Menu"]
    );
  }

  /**
   * Hook runs *after* base class delete. Remove all items for menu.
   */
  protected async onAfterDelete(deletedId: string): Promise<void> {
    const { fastify } = this;
    const checkItems = await this.fastify.elastic.search({
      index: "restaurant_menu_items",
      query: {
        term: {
          "menu_id.keyword": deletedId,
        },
      },
    });
    console.log("Items to be deleted:", checkItems.hits.hits);

    await this.fastify.elastic.deleteByQuery({
      index: "restaurant_menu_items",
      body: {
        query: {
          term: {
            "menu_id.keyword": deletedId,
          },
        },
      },
    });
  }
}
