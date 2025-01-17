// src/crud/baseCRUD.ts
import { FastifyInstance, FastifyRequest, FastifyReply } from "fastify";
import { z, ZodSchema } from "zod";
import { paginationDTO, PaginationDTO } from "~/dtos/requestDTOs";
import {
  dataResponseDTO,
  defaultResponseDTO,
  paginatedDataListResponseDTO,
} from "~/dtos/responseDTOs";
import { AnyPgTable } from "drizzle-orm/pg-core";
import { PostgresService } from "~/services/pgService";
import { ElasticsearchService } from "~/services/elasticsearchService";

type ResponseSchema = ZodSchema<any>;
type RequestSchema = ZodSchema<any>;

export class CRUDBase<
  M extends AnyPgTable,
  T extends RequestSchema,
  R extends ResponseSchema,
> {
  constructor(
    public fastify: FastifyInstance,
    public pgService: PostgresService<M>,
    public esService: ElasticsearchService<T>,
    public idField: string,
    public requestDTO: T,
    public responseDTO: R,
    public tags: string[]
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
    req: FastifyRequest<{ Querystring: PaginationDTO }>,
    res: FastifyReply
  ) {
    const { page, page_size: pageSize } = req.query;
    const offset = (page - 1) * pageSize;

    try {
      const esResult = await this.esService.search(
        { match_all: {} },
        offset,
        pageSize
      );

      return this.formatPaginatedResponse(esResult, page, pageSize);
    } catch (e) {
      this.fastify.log.error(`handleGetAll error: ${e}`);
      return res.status(500).send({ error: `Something went wrong: ${e}` });
    }
  }

  async handleGetOne(
    req: FastifyRequest<{ Params: { id: string } }>,
    res: FastifyReply
  ) {
    const { id } = req.params;

    try {
      const esResult = await this.esService.getById(id);

      const result = esResult.hits.hits;
      if (result.length === 0) {
        return res
          .status(404)
          .send({ error: `No ${this.esService.index} found.` });
      }

      const data = result.map((hit) => ({
        [this.idField]: hit._id,
        ...hit._source,
      }));
      return res.status(200).send({ data: data[0] });
    } catch (e) {
      this.fastify.log.error(`handleGetOne error: ${e}`);
      return res.status(500).send({ error: `Something went wrong: ${e}` });
    }
  }

  async handleCreate(req: FastifyRequest, res: FastifyReply) {
    try {
      const result = await this.pgService.transaction(async (tx) => {
        const inserted = await this.pgService.create(
          req.body as M["$inferInsert"],
          tx
        );

        const insertedId = inserted[this.idField];

        await this.esService.create(insertedId, req.body);
        await this.onAfterCreate(insertedId, inserted, req);

        return inserted;
      });

      return res.status(200).send({ data: result[this.idField] });
    } catch (e) {
      this.fastify.log.error(
        `Error in POST /${this.esService.index}: ${(e as Error).message}`
      );
      return res
        .status(500)
        .send({ error: `Something went wrong: ${(e as Error).message}` });
    }
  }

  async handleUpdate(
    req: FastifyRequest<{ Params: { id: string } }>,
    res: FastifyReply
  ) {
    const { id } = req.params;
    const updateData = req.body;

    try {
      const updated = await this.pgService.transaction(async (tx) => {
        const result = await this.pgService.update(
          id,
          updateData as Partial<M["$inferInsert"]>,
          tx
        );

        if (result.length === 0) {
          return null;
        }

        await this.esService.update(id, updateData);

        await this.onAfterUpdate(id, result, req);

        return result;
      });

      if (!updated) {
        return res
          .status(404)
          .send({ error: `No ${this.esService.index} found.` });
      }

      return res.status(200).send({ data: id });
    } catch (e) {
      this.fastify.log.error(`handleUpdate error: ${e}`);
      return res.status(500).send({ error: `Update failed: ${e}` });
    }
  }

  async handleDelete(
    req: FastifyRequest<{ Params: { id: string } }>,
    res: FastifyReply
  ) {
    const { id } = req.params;

    try {
      const deleted = await this.pgService.transaction(async (tx) => {
        const result = await this.pgService.delete(id, tx);

        if (result.length === 0) {
          return null;
        }

        await this.esService.delete(id);

        await this.onAfterDelete(id);

        return result;
      });

      if (!deleted) {
        return res
          .status(404)
          .send({ error: `No ${this.esService.index} found.` });
      }

      return res.status(200).send({ data: id });
    } catch (e) {
      this.fastify.log.error(`handleDelete error: ${e}`);
      return res.status(500).send({ error: `Delete failed: ${e}` });
    }
  }

  public formatPaginatedResponse(
    esResult: any,
    page: number,
    pageSize: number
  ) {
    const hits = esResult.hits.hits;
    const totalItems = esResult.hits.total?.value ?? hits.length;
    const totalPages = Math.ceil(totalItems / pageSize);

    const data = hits.map((hit: any) => ({
      [this.idField]: hit._id,
      ...hit._source,
    }));

    console.log(data)

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
}
