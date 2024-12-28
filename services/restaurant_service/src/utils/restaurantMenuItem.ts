import { FastifyInstance, FastifyRequest, FastifyReply } from "fastify";
import { z } from "zod";
import { restaurantSettingsTable, restaurantsTable } from "~/db/schema";
import {
  restaurantRequestDTO,
  restaurantResponseDTO,
} from "~/dtos/restaurant_dtos";
import { CRUDBase } from "./baseCRUD";

export class RestaurantCRUD extends CRUDBase<
  typeof restaurantsTable,
  typeof restaurantResponseDTO,
  typeof restaurantRequestDTO
> {
  constructor(fastify: FastifyInstance) {
    super(
      fastify,
      restaurantsTable,
      "restaurants",
      "restaurant_id",
      restaurantResponseDTO,
      restaurantRequestDTO,
      ["Restaurant"]
    );
  }

  /**
   * Override handleCreate:
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
        // 1) Insert into main "restaurants" table (same logic as base):
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
}
