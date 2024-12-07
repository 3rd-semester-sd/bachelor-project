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

fastify.register(fastifySwagger, {
  openapi: {
    info: {
      title: "Restaurant API",
      description: "Resturant API",
      version: "0.0.1",
    },
    servers: [],
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
    docExpansion: "full",
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

fastify.setValidatorCompiler(validatorCompiler);
fastify.setSerializerCompiler(serializerCompiler);

// This loads all plugins defined in plugins
fastify.register(dbPlugin, {
  databaseUrl: process.env.RESTAURANT_DATABASE_URL!,
});

// This loads all plugins defined in routes
// define your routes in one of these
void fastify.register(AutoLoad, {
  dir: join(__dirname, "routes"),
});

export const app = fastify.withTypeProvider<ZodTypeProvider>();
