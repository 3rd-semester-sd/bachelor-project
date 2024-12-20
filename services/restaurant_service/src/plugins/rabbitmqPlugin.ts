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
