// plugins/rabbitmqPlugin.ts

import { FastifyInstance, FastifyPluginAsync } from "fastify";
import fp from "fastify-plugin";
import { Channel } from "amqplib";

export type RabbitMQInitializerOptions = {
  exchangeName: string;
  exchangeType: "fanout" | "direct" | "topic" | "headers";
  queueName: string;
  routingKey: string;
  durable?: boolean;
  shouldConsume?: boolean;
};
/// Initialize rabbitmq, to ensure bot the exchange and queue are created
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
        channel.consume(q.queue, async (msg) => {
          if (!msg) return;
          try {
            const data = JSON.parse(msg.content.toString());
            // data could look like:
            // {
            //   saga_id: string,
            //   restaurant_id: string,
            //   result: "success" | "failure",
            //   error?: string
            // }

            if (data.result === "success") {
              fastify.log.info(`Successfully saved restaurant:${{ ...msg }}`);
              // 1) Mark restaurant as ACTIVE in DB (if you maintain a status column).
              // 2) Possibly log success or do any final steps.
            } else {
              fastify.log.info(`Did not save restaurant:${msg}`);
              // 1) We have a failure. We need to do a compensation step:
              //    - e.g., delete the restaurant row, or set status to "FAILED"
              //    - optionally remove from Elasticsearch
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
