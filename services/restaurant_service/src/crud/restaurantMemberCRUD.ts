// restaurantMenuItemCRUD.ts
import { FastifyInstance } from "fastify";
import { restaurantMembersTable } from "~/db/schema";
import { CRUDBase } from "./baseCRUD";

import {
  restaurantMemberDTO,
  restaurantMemberRequestDTO,
} from "~/dtos/restaurantMemberDTOs";
import { ElasticsearchService } from "~/services/elasticsearchService";
import { PostgresService } from "~/services/pgService";

export class RestaurantMemberCRUD extends CRUDBase<
  typeof restaurantMembersTable,
  typeof restaurantMemberRequestDTO,
  typeof restaurantMemberDTO
> {
  constructor(fastify: FastifyInstance) {
    // Initialize services with fastify instance
    const pgService = new PostgresService(
      fastify,
      restaurantMembersTable,
      "member_id"
    );
    const esService = new ElasticsearchService<typeof restaurantMemberDTO>(
      fastify,
      "restaurant_members"
    );
    super(
      fastify,
      pgService,
      esService,
      "member_id",
      restaurantMemberRequestDTO,
      restaurantMemberDTO,
      ["Restaurant member"]
    );
  }

  /**
   * Hook runs *after* base class delete. Remove all items for menu.
   */
  protected async onAfterDelete(deletedId: string): Promise<void> {
    const { fastify } = this;

    // delete menu related to restaurant
    await this.fastify.elastic.deleteByQuery({
      index: "menus",
      body: {
        query: {
          term: {
            restaurant_id: deletedId,
          },
        },
      },
    });

    // delete all related menu_items to restaurant
    await this.fastify.elastic.deleteByQuery({
      index: "menu_items",
      body: {
        query: {
          term: {
            restaurant_id: deletedId,
          },
        },
      },
    });
    await this.fastify.elastic.deleteByQuery({
      index: "restaurant_menu_items",
      body: {
        query: {
          term: {
            menu_id: deletedId,
          },
        },
      },
    });
  }
}
