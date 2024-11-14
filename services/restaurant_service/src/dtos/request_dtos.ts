import { z } from "zod";

export const PaginationSchema = z.object({
  page: z
    .string()
    .transform((val) => parseInt(val, 10))
    .default("1")
    .pipe(z.number().int().positive()),
  pageSize: z
    .string()
    .transform((val) => parseInt(val, 10))
    .default("10")
    .pipe(z.number().int().positive().max(100)),
});
