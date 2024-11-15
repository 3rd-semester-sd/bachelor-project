import { z } from "zod";

export const dataResponseDTO = <T extends z.ZodTypeAny>(itemSchema: T) =>
  z.object({
    data: itemSchema
      .nullable()
      .optional()
      .describe("Default response with a single data entry"),
  });

export const dataListResponseDTO = <T extends z.ZodTypeAny>(inputDTO: T) =>
  z
    .object({
      data: z.array(inputDTO).optional(),
    })
    .describe("Response with a list of data entries");

export const paginatedDataListResponseDTO = <T extends z.ZodTypeAny>(
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

export const defaultResponseDTO = z.object({
  data: z.union([z.string().uuid(), z.number()]).nullable().default(null),
  message: z.string().optional().default("Ok."),
});

export type DataResponseDTO<T extends z.ZodTypeAny> = z.infer<
  ReturnType<typeof dataResponseDTO<T>>
>;
export type DataListResponseDTO<T extends z.ZodTypeAny> = z.infer<
  ReturnType<typeof dataListResponseDTO<T>>
>;

export type PaginatedDataListResponseDTO<T extends z.ZodTypeAny> = z.infer<
  ReturnType<typeof paginatedDataListResponseDTO<T>>
>;

export type DefaultCreatedResponse = z.infer<typeof defaultResponseDTO>;
