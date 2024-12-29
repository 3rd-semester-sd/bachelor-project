import { app } from '../src/app';
import { FastifyInstance } from 'fastify';

export async function buildApp(): Promise<FastifyInstance> {
  const server = app;
  
  // Clear before/after each test if needed
  beforeEach(async () => {
    // Clear your test database/elasticsearch here if needed
  });

  afterAll(async () => {
    await server.close();
  });

  return server;
}