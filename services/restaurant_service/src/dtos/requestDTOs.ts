import { z } from "zod";

export const paginationDTO = z.object({
  page: z
    .string()
    .transform((val) => parseInt(val, 10))
    .default("1")
    .pipe(z.number().int().positive()),
  page_size: z
    .string()
    .transform((val) => parseInt(val, 10))
    .default("10")
    .pipe(z.number().int().positive().max(100)),
});
export const searchBodyDTO = z.object({
  input: z.string(),
});

export type PaginationDTO = z.infer<typeof paginationDTO>;
export type SearchBodyDTO = z.infer<typeof searchBodyDTO>;
