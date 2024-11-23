import {
  FastifyPluginAsync,
  FastifyPluginOptions,
  RawServerDefault,
} from "fastify";
import { ZodTypeProvider } from "fastify-type-provider-zod";

export type DefaultOptions = {};

export type BasePlugin<O extends FastifyPluginOptions = DefaultOptions> =
  FastifyPluginAsync<O, RawServerDefault, ZodTypeProvider>;
