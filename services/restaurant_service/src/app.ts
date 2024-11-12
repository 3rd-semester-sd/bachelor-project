import fastifySwagger from "@fastify/swagger";
import fastifySwaggerUI from "@fastify/swagger-ui";
import Fastify from "fastify";
import {
  jsonSchemaTransform,
  serializerCompiler,
  validatorCompiler,
  ZodTypeProvider,
} from "fastify-type-provider-zod";

const fastify = Fastify();

fastify.register(fastifySwagger, {
  openapi: {
    info: {
      title: "Restaurant API",
      description: "Restaurant API",
      version: "0.0.1",
    },
    servers: [],
  },
  transform: jsonSchemaTransform,
});

fastify.register(fastifySwaggerUI, {
  routePrefix: "/docs",
});

fastify.setValidatorCompiler(validatorCompiler);
fastify.setSerializerCompiler(serializerCompiler);

export const app = fastify.withTypeProvider<ZodTypeProvider>();
