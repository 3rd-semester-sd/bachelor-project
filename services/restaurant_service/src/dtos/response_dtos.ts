import { z } from "zod";

const UUIDSchema = z.string().uuid();
const SuccessSchema = z.boolean().default(true);
const MessageSchema = z.string().optional();

export const DataResponseSchema = <T extends z.ZodTypeAny>(itemSchema: T) =>
  z.object({
    data: itemSchema
      .nullable()
      .optional()
      .describe("Default response with a single data entry"),
  });

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

export type DataResponse<T extends z.ZodTypeAny> = z.infer<
  ReturnType<typeof DataResponseSchema<T>>
>;

export type DataListResponse<T extends z.ZodTypeAny> = z.infer<
  ReturnType<typeof DataListResponseSchema<T>>
>;

export const PaginatedDataListResponseSchema = <T extends z.ZodTypeAny>(
  itemSchema: T
) =>
  z
    .object({
      data: z.array(itemSchema).optional(),
      pagination: z
        .object({
          total_items: z.number(),
          total_pages: z.number(),
          current_page: z.number(),
          page_size: z.number(),
        })
        .describe("Pagination metadata"),
    })
    .describe("Response with a list of data entries and pagination metadata");

export type SuccessAndMessage = z.infer<typeof SuccessAndMessageSchema>;
export type EmptyDefaultResponse = z.infer<typeof EmptyDefaultResponseSchema>;
export type DefaultCreatedResponse = z.infer<
  typeof DefaultCreatedResponseSchema
>;
