import "dotenv/config";
import path, { join } from "path";
import fastifySwagger from "@fastify/swagger";
import fastifySwaggerUI from "@fastify/swagger-ui";
import Fastify from "fastify";
import {
  jsonSchemaTransform,
  serializerCompiler,
  validatorCompiler,
  ZodTypeProvider,
} from "fastify-type-provider-zod";
import AutoLoad from "@fastify/autoload";
import { dbPlugin } from "./plugins/dbPlugin";
import fastifyElasticsearch from "@fastify/elasticsearch";
import fastifyAmqp from "fastify-amqp";
import rabbitmqPlugin from "./plugins/rabbitmqPlugin";

const fastify = Fastify({
  logger:
    process.env.NODE_ENV === "DEV"
      ? {
          level: "info",
          transport: {
            target: "pino-pretty", // human-readable logs in development
          },
        }
      : true, // default logs for prod
  bodyLimit: 1024 * 1024 * 1024,
});

// Register Swagger with security scheme
fastify.register(fastifySwagger, {
  openapi: {
    info: {
      title: "Restaurant API",
      description: "Restaurant API",
      version: "0.0.1",
    },
    servers: [
      {
        url: "/restaurant-service",
      },
    ],
    components: {
      securitySchemes: {
        bearerAuth: {
          type: "http",
          scheme: "bearer",
          bearerFormat: "JWT", // Optional, for better documentation
        },
      },
    },
  },
  transform: jsonSchemaTransform,
});

fastify.register(fastifySwaggerUI, {
  routePrefix: "/docs",
  baseDir:
    process.env.NODE_ENV === "PROD"
      ? path.resolve(__dirname, "static")
      : undefined,

  uiConfig: {
    docExpansion: "list",
    deepLinking: false,
  },
  uiHooks: {
    onRequest: function (request, reply, next) {
      next();
    },
    preHandler: function (request, reply, next) {
      next();
    },
  },
  transformStaticCSP: (header) => header,
  transformSpecification: (swaggerObject, request, reply) => {
    return swaggerObject;
  },
  transformSpecificationClone: true,
});

// Compiler settings
fastify.setValidatorCompiler(validatorCompiler);
fastify.setSerializerCompiler(serializerCompiler);

// Register plugins
fastify.register(dbPlugin, {
  databaseUrl: process.env.RESTAURANT_DATABASE_URL!,
});
fastify.register(fastifyElasticsearch, {
  node: process.env.RESTAURANT_ES_URL,
});
fastify.register(fastifyAmqp, {
  hostname: process.env.RESTAURANT_RABBIT_HOSTNAME,
  port: Number(process.env.RESTAURANT_RABBIT_PORT),
  username: process.env.RESTAURANT_RABBIT_USERNAME,
  password: process.env.RESTAURANT_RABBIT_PASSWORD,
});
fastify.register(rabbitmqPlugin, {
  exchangeName: "new_restaurant_exchange",
  exchangeType: "fanout",
  queueName: "new_restaurant_queue",
  routingKey: "",
});
fastify.register(rabbitmqPlugin, {
  exchangeName: "embedding_result_exchange",
  exchangeType: "fanout",
  queueName: "restaurant_service_embedding_result",
  routingKey: "",
  shouldConsume: true,
});

// Auto-load routes
void fastify.register(AutoLoad, {
  dir: join(__dirname, "routes"),
  dirNameRoutePrefix: (folderParent, folderName) => {
    return `api/${folderName
      .replace(/([a-z])([A-Z])/g, "$1-$2")
      .toLowerCase()}`;
  },
  prefix: "restaurant-service",
});

export const app = fastify.withTypeProvider<ZodTypeProvider>();
