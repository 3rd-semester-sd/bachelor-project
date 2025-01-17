// src/crud/restaurantCRUD.ts
import { FastifyInstance, FastifyRequest, FastifyReply } from "fastify";
import { z } from "zod";
import { restaurantSettingsTable, restaurantsTable } from "~/db/schema";
import {
  restaurantRequestDTO,
  restaurantResponseDTO,
} from "~/dtos/restaurantDTOs";
import { CRUDBase } from "./baseCRUD";
import { PostgresService } from "~/services/pgService";
import { ElasticsearchService } from "~/services/elasticsearchService";

export class RestaurantCRUD extends CRUDBase<
  typeof restaurantsTable,
  typeof restaurantRequestDTO,
  typeof restaurantResponseDTO
> {
  private settingsPgService: PostgresService<typeof restaurantSettingsTable>;

  constructor(
    fastify: FastifyInstance,
    pgService: PostgresService<typeof restaurantsTable>,
    esService: ElasticsearchService<typeof restaurantResponseDTO>
  ) {
    super(
      fastify,
      pgService,
      esService,
      "restaurant_id",
      restaurantRequestDTO,
      restaurantResponseDTO,
      ["Restaurant"]
    );

    // Initialize additional services
    this.settingsPgService = new PostgresService(
      fastify,
      restaurantSettingsTable,
      "restaurant_id"
    );
  }

  /**
   * Override handleCreate to keep everything in one transaction:
   * - Insert into restaurant_settings
   * - Publish RabbitMQ message
   */
  async handleCreate(
    req: FastifyRequest<{ Body: z.infer<typeof restaurantRequestDTO> }>,
    res: FastifyReply
  ) {
    try {
      const { amqp } = this.fastify;

      // Start transaction
      const result = await this.pgService.transaction(async (tx) => {
        // 1) Insert into main "restaurants" table:
        const user_id = req.headers["x-user-id"] as string;
        if (!user_id) {
          throw new Error("Missing x-user-id header");
        }

        const inserted = await this.pgService.create(
          { member_id: user_id, ...req.body },
          tx
        );

        const newRestaurantId = inserted[this.idField];

        // 2) Insert into the "restaurant_settings" table:
        await this.settingsPgService.create(
          {
            restaurant_id: newRestaurantId,
            ...req.body.restaurant_settings,
          },
          tx
        );

        const document = {
          member_id: user_id,
          restaurant_id: newRestaurantId,
          ...req.body,
        };

        // 3) Index in Elasticsearch:
        await this.esService.create(newRestaurantId, document);

        // 4) Publish RabbitMQ message:
        const msg = {
          restaurant_id: newRestaurantId,
          restaurant_name: req.body.restaurant_name,
          description: req.body.restaurant_description,
          saga_id: newRestaurantId,
          timestamp: new Date().toISOString(),
        };

        const msgBuffer = Buffer.from(JSON.stringify(msg));
        const exchangeName = "new_restaurant_exchange";
        const routingKey = "";

        const publishOk = amqp.channel.publish(
          exchangeName,
          routingKey,
          msgBuffer,
          {
            persistent: true,
          }
        );
        if (!publishOk) {
          this.fastify.log.error(
            "Failed to publish message to RabbitMQ exchange"
          );
          throw new Error("Failed to publish message to RabbitMQ");
        }

        return inserted;
      });

      // Return the newly created ID
      return res.status(200).send({ data: result[this.idField] });
    } catch (e) {
      this.fastify.log.error(
        `Error in POST /${this.esService.index}: ${(e as Error).message}`
      );
      return res
        .status(500)
        .send({ error: `Something went wrong: ${(e as Error).message}` });
    }
  }

  protected async onAfterDelete(deletedId: string): Promise<void> {
    // Delete menu related to restaurant
    const esResult = await this.fastify.elastic.search({
      index: "restaurant_menu",
      query: {
        match: {
          restaurant_id: deletedId,
        },
      },
    });

    for (const result of esResult.hits.hits as any[]) {
      await this.fastify.elastic.deleteByQuery({
        index: "restaurant_menu",
        body: {
          query: {
            match: {
              restaurant_id: result._source.restaurant_id,
            },
          },
        },
      });

      if (result._source.menu_items) {
        const menu_items = result._source.menu_items;
        for (const item of menu_items) {
          await this.fastify.elastic.deleteByQuery({
            index: "restaurant_menu_items",
            body: {
              query: {
                match: {
                  menu_id: item.menu_id,
                },
              },
            },
          });
        }
      }
    }
  }
}
