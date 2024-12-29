import { FastifyInstance, FastifyRequest, FastifyReply } from "fastify";
import { z } from "zod";
import { restaurantSettingsTable, restaurantsTable } from "~/db/schema";
import {
  restaurantRequestDTO,
  restaurantResponseDTO,
} from "~/dtos/restaurantDTOs";
import { CRUDBase } from "./baseCRUD";
import { RestaurantMenu } from "~/dtos/restaurantMenuDTOs";

export class RestaurantCRUD extends CRUDBase<
  typeof restaurantsTable,
  typeof restaurantRequestDTO,
  typeof restaurantResponseDTO
> {
  constructor(fastify: FastifyInstance) {
    super(
      fastify,
      restaurantsTable,
      "restaurants",
      "restaurant_id",
      restaurantRequestDTO,
      restaurantResponseDTO,
      ["Restaurant"]
    );
  }

  /**
   * Override handleCreate, to keep everything in one transaction:
   * - Insert into restaurant_settings
   * - Publish RabbitMQ message
   */
  async handleCreate(
    req: FastifyRequest<{ Body: z.infer<typeof restaurantRequestDTO> }>,
    res: FastifyReply
  ) {
    try {
      const { db, elastic, amqp } = this.fastify;

      // Start transaction
      const result = await db.transaction(async (tx) => {
        // 1) Insert into main "restaurants" table:
        const inserted = await tx
          .insert(this.table)
          .values(req.body)
          .returning({
            [this.idField]: (this.table as any)[this.idField],
          });

        const newRestaurantId = inserted[0][this.idField];

        // 2) Insert into the "restaurant_settings" table:
        await tx.insert(restaurantSettingsTable).values({
          restaurant_id: newRestaurantId,
          ...req.body.restaurant_settings,
        });

        // 3) Index in Elasticsearch:
        await elastic.index({
          index: this.esIndex,
          id: newRestaurantId,
          document: req.body,
        });

        // 4) Publish RabbitMQ message:
        const msg = {
          restaurant_id: newRestaurantId,
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
      return res.status(200).send({ data: result[0][this.idField] });
    } catch (e) {
      this.fastify.log.error(
        `Error in POST /${this.esIndex}: ${(e as Error).message}`
      );
      return res
        .status(500)
        .send({ error: `something went wrong: ${(e as Error).message}` });
    }
  }
  protected async onAfterDelete(deletedId: string): Promise<void> {
    // delete menu related to restaurant

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
