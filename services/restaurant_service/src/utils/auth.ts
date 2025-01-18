import { FastifyRequest } from "fastify";

// Simple utility function to extract required headers
export function extractHeader(req: FastifyRequest, headerName: string): string {
  const headerValue = req.headers[headerName] as string | undefined;

  if (!headerValue) {
    throw new Error(`Missing ${headerName} header`);
  }

  return headerValue;
}

// Convenience function for user ID
export function extractUserId(req: FastifyRequest): string {
  return extractHeader(req, "x-user-id");
}
