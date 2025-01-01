import { FastifyInstance, FastifyPluginAsync } from "fastify";
import fp from "fastify-plugin";
import { Channel } from "amqplib";
import { restaurantsTable } from "~/db/schema";
import { eq } from "drizzle-orm";
import { RestaurantStatus } from "~/db/enums";

export type RabbitMQInitializerOptions = {
  exchangeName: string;
  exchangeType: "fanout" | "direct" | "topic" | "headers";
  queueName: string;
  routingKey: string;
  durable?: boolean;
  shouldConsume?: boolean;
};
// Initialize rabbitmq, to ensure both the exchange and queue are created
const rabbitmqInitializer: FastifyPluginAsync<RabbitMQInitializerOptions> = fp(
  async (fastify: FastifyInstance, options: RabbitMQInitializerOptions) => {
    const {
      exchangeName,
      exchangeType,
      queueName,
      routingKey,
      durable = true,
      shouldConsume = false,
    } = options;

    try {
      // Access the AMQP connection from fastify-amqp
      const connection = fastify.amqp;

      // Create a channel
      const channel: Channel = await connection.connection.createChannel();

      // Declare the exchange
      await channel.assertExchange(exchangeName, exchangeType, { durable });
      fastify.log.info(
        `Exchange "${exchangeName}" of type "${exchangeType}" declared.`
      );

      // Declare the queue
      const q = await channel.assertQueue(queueName, { durable });
      fastify.log.info(`Queue "${queueName}" declared.`);

      // Bind the queue to the exchange with the routing key
      await channel.bindQueue(q.queue, exchangeName, routingKey);
      fastify.log.info(
        `Queue "${queueName}" bound to exchange "${exchangeName}" with routing key "${routingKey}".`
      );

      if (shouldConsume) {
        fastify.log.info(
          `bound consumer for queue: "${queueName}", exchange: "${exchangeName}"  `
        );
        // Add consumer
        channel.consume(q.queue, async (msg) => {
          if (!msg) return;
          try {
            const data = JSON.parse(msg.content.toString());
            console.log(data);
            // If the result is success, update restaurant status in postgres
            if (data.result === "success") {
              fastify.log.info(`Successfully saved restaurant:${{ ...msg }}`);
              await fastify.db
                .update(restaurantsTable)
                .set({ restaurant_status: RestaurantStatus.ACTIVE })
                .where(eq(restaurantsTable.restaurant_id, data.restaurant_id));
            } else {
              // If the result is not success remove from postgres and elastic search
              fastify.log.info(`Did not save restaurant:${msg}`);
              await fastify.db
                .delete(restaurantsTable)
                .where(eq(restaurantsTable.restaurant_id, data.restaurant_id));

              await fastify.elastic.delete({
                index: "restaurants",
                id: data.restaurant_id,
              });
            }
          } catch (err) {
            fastify.log.error(`Error in consumer: ${err}`);
          } finally {
            channel.ack(msg);
          }
        });
        return;
      }
      await channel.close();
    } catch (error) {
      fastify.log.error(
        `Error initializing RabbitMQ: ${(error as Error).message}`
      );
      throw error;
    }
  }
);

export default rabbitmqInitializer;
