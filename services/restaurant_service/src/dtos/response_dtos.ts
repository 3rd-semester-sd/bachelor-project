import { z } from "zod";

const UUIDSchema = z.string().uuid();
const SuccessSchema = z.boolean().default(true);
const MessageSchema = z.string().optional();

export const DataResponseSchema = z
  .object({
    data: z.unknown().nullable().optional(),
  })
  .describe("Default response with a single data entry");

export const DataListResponseSchema = <T extends z.ZodTypeAny>(itemSchema: T) =>
  z
    .object({
      data: z.array(itemSchema).optional(),
    })
    .describe("Response with a list of data entries");

export const SuccessAndMessageSchema = z.object({
  success: SuccessSchema,
  message: MessageSchema.default("Success!"),
});

export const EmptyDefaultResponseSchema = SuccessAndMessageSchema.extend({
  data: z.null().default(null),
}).describe("Empty response with success and message");

export const DefaultCreatedResponseSchema = z.object({
  data: z.union([UUIDSchema, z.number()]).nullable().default(null),
  message: MessageSchema.default("Created successfully!"),
});

export type DataResponse = z.infer<typeof DataResponseSchema>;
export type DataListResponse = z.infer<typeof DataListResponseSchema>;
export type SuccessAndMessage = z.infer<typeof SuccessAndMessageSchema>;
export type EmptyDefaultResponse = z.infer<typeof EmptyDefaultResponseSchema>;
export type DefaultCreatedResponse = z.infer<
  typeof DefaultCreatedResponseSchema
>;
