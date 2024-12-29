import { FastifyInstance, FastifyRequest, FastifyReply } from "fastify";
import { eq } from "drizzle-orm";
import { z } from "zod";
import { paginationDTO } from "~/dtos/requestDTOs";
import {
  dataResponseDTO,
  defaultResponseDTO,
  paginatedDataListResponseDTO,
} from "~/dtos/responseDTOs";
import { AnyPgTable } from "drizzle-orm/pg-core";

type ResponseSchema = z.ZodObject<any>;
type RequestSchema = z.ZodObject<any>;

export class CRUDBase<
  M extends AnyPgTable,
  T extends RequestSchema,
  R extends ResponseSchema,
> {
  constructor(
    protected fastify: FastifyInstance,
    protected table: M,
    protected esIndex: string,
    protected idField: string,
    protected requestDTO: T,
    protected responseDTO: R,
    protected tags: string[]
  ) {}
  /**
   * Hook that runs *after* successfully creating a record in DB.
   * By default, it does nothing. Derived classes can override this.
   */
  protected async onAfterCreate(
    insertedId: string,
    insertedData: Partial<M["$inferInsert"]>,
    req: FastifyRequest
  ): Promise<void> {
    // no-op in base class
  }
  protected async onAfterDelete(insertedId: string): Promise<void> {
    // no-op in base class
  }
  protected async onAfterUpdate(
    insertedId: string,
    insertedData: Partial<M["$inferInsert"]>,
    req: FastifyRequest
  ): Promise<void> {
    // no-op in base class
  }
  async handleGetAll(
    req: FastifyRequest<{ Querystring: { page: number; page_size: number } }>,
    res: FastifyReply
  ) {
    const { page, page_size: pageSize } = req.query;
    const offset = (page - 1) * pageSize;

    try {
      const esResult = await this.fastify.elastic.search<T>({
        index: this.esIndex,
        query: { match_all: {} },
        from: offset,
        size: pageSize,
      });

      return this.formatPaginatedResponse(esResult, page, pageSize);
    } catch (e) {
      return res.status(500).send({ error: `something went wrong: ${e}` });
    }
  }

  async handleGetOne(
    req: FastifyRequest<{ Params: { id: string } }>,
    res: FastifyReply
  ) {
    const { id } = req.params;

    try {
      const esResult = await this.fastify.elastic.search<T>({
        index: this.esIndex,
        query: { match: { _id: id } },
      });

      const result = esResult.hits.hits;
      if (result.length === 0) {
        return res.status(404).send({ error: `No ${this.esIndex} found.` });
      }

      const data = result.map((hit) => ({
        [this.idField]: hit._id,
        ...hit._source,
      }));
      return res.status(200).send({ data: data[0] });
    } catch (e) {
      return res.status(500).send({ error: `something went wrong: ${e}` });
    }
  }

  async handleCreate(req: FastifyRequest, res: FastifyReply) {
    try {
      const result = await this.fastify.db.transaction(async (tx) => {
        const inserted = await tx
          .insert(this.table)
          .values(req.body as M["$inferInsert"])
          .returning({
            [this.idField]: (this.table as unknown as Record<string, any>)[
              this.idField
            ],
          });

        const insertedId = inserted[0][this.idField];

        await this.fastify.elastic.index({
          index: this.esIndex,
          id: insertedId,
          document: req.body,
        });

        await this.onAfterCreate(insertedId, inserted, req);

        return inserted;
      });

      return res.status(200).send({ data: result[0][this.idField] });
    } catch (e) {
      this.fastify.log.error(
        `Error in POST /${this.esIndex}: ${(e as Error).message}`
      );
      return res
        .status(500)
        .send({ error: `something went wrong: ${(e as Error).message}` });
    }
  }

  async handleUpdate(
    req: FastifyRequest<{ Params: { id: string } }>,
    res: FastifyReply
  ) {
    const { id } = req.params;
    const updateData = req.body;

    try {
      await this.fastify.db.transaction(async (tx) => {
        const result = await tx
          .update(this.table)
          .set(updateData as Partial<M["$inferInsert"]>)
          .where(
            eq((this.table as unknown as Record<string, any>)[this.idField], id)
          )
          .returning();

        if (result.length === 0) {
          return res.status(404).send({ error: `No ${this.esIndex} found.` });
        }

        await this.fastify.elastic.update({
          index: this.esIndex,
          id: id,
          doc: updateData,
        });

        await this.onAfterUpdate(id, result, req);
      });
      return res.status(200).send({ data: id });
    } catch (e) {
      return res.status(500).send({ error: `Update failed: ${e}` });
    }
  }

  async handleDelete(
    req: FastifyRequest<{ Params: { id: string } }>,
    res: FastifyReply
  ) {
    const { id } = req.params;

    try {
      await this.fastify.db.transaction(async (tx) => {
        const result = await tx
          .delete(this.table)
          .where(
            eq((this.table as unknown as Record<string, any>)[this.idField], id)
          )
          .returning();

        if (result.length === 0) {
          return res.status(404).send({ error: `No ${this.esIndex} found.` });
        }

        await this.fastify.elastic.delete({
          index: this.esIndex,
          id: id,
        });

        await this.onAfterDelete(id);
      });
      return res.status(200).send({ data: id });
    } catch (e) {
      return res.status(500).send({ error: `Delete failed: ${e}` });
    }
  }

  private formatPaginatedResponse(
    esResult: any,
    page: number,
    pageSize: number
  ) {
    const hits = esResult.hits.hits;
    const totalItems = hits.length ?? 0;
    const totalPages = Math.ceil(totalItems / pageSize);

    const data = hits.map((hit: any) => ({
      [this.idField]: hit._id,
      ...hit._source,
    }));

    return {
      data,
      pagination: {
        total_items: totalItems,
        total_pages: totalPages,
        current_page: page,
        page_size: pageSize,
      },
    };
  }

  registerRoutes() {
    const commonResponses = {
      500: z.object({ error: z.string() }),
    };

    this.fastify.route({
      method: "GET",
      url: "",
      schema: {
        tags: this.tags,
        querystring: paginationDTO,
        response: {
          200: paginatedDataListResponseDTO(this.responseDTO),
          ...commonResponses,
        },
      },
      handler: this.handleGetAll.bind(this),
    });

    this.fastify.route({
      method: "GET",
      url: "/:id",
      schema: {
        tags: this.tags,
        params: z.object({ id: z.string().uuid() }),
        response: {
          200: dataResponseDTO(this.responseDTO),
          ...commonResponses,
        },
      },
      handler: this.handleGetOne.bind(this),
    });

    this.fastify.route({
      method: "POST",
      url: "",
      schema: {
        tags: this.tags,
        body: this.requestDTO,
        response: {
          200: defaultResponseDTO,
          ...commonResponses,
        },
      },
      handler: this.handleCreate.bind(this),
    });

    this.fastify.route({
      method: "PATCH",
      url: "/:id",
      schema: {
        tags: this.tags,
        params: z.object({ id: z.string().uuid() }),
        body: this.requestDTO.partial(),
        response: {
          200: defaultResponseDTO,
          ...commonResponses,
        },
      },
      handler: this.handleUpdate.bind(this),
    });

    this.fastify.route({
      method: "DELETE",

      url: "/:id",
      schema: {
        tags: this.tags,
        params: z.object({ id: z.string().uuid() }),
        response: {
          200: defaultResponseDTO,
          ...commonResponses,
        },
      },
      handler: this.handleDelete.bind(this),
    });
  }
}
