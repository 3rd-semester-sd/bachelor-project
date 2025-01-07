import { FastifyInstance, FastifyRequest, FastifyReply } from "fastify";
import { z } from "zod";
import { paginationDTO } from "~/dtos/requestDTOs";
import {
  dataResponseDTO,
  defaultResponseDTO,
  paginatedDataListResponseDTO,
} from "~/dtos/responseDTOs";
import { AnyPgTable } from "drizzle-orm/pg-core";
import { PostgresService } from "~/services/pgService";
import { ElasticsearchService } from "~/services/elasticsearchService";

type ResponseSchema = z.ZodObject<any>;
type RequestSchema = z.ZodObject<any>;

export class CRUDBase<
  M extends AnyPgTable,
  T extends RequestSchema,
  R extends ResponseSchema,
> {
  constructor(
    public fastify: FastifyInstance,
    protected pgService: PostgresService<M>,
    protected esService: ElasticsearchService<T>,
    protected idField: string,
    protected requestDTO: T,
    protected responseDTO: R,
    protected tags: string[]
  ) {
    this.pgService = pgService; // store the instance
    this.esService = esService;
  }
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
      const esResult = await this.esService.search(
        { match_all: {} },
        offset,
        pageSize
      );
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
      return res.status(500).send({ error: `something went wrong: ${e}` });
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
        await this.onAfterCreate(insertedId, inserted.id, req);

        return inserted;
      });

      return res.status(200).send({ data: result[this.idField] });
    } catch (e) {
      this.fastify.log.error(
        `Error in POST /${this.esService.index}: ${(e as Error).message}`
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
      await this.pgService.transaction(async (tx) => {
        const result = await this.pgService.update(
          id,
          updateData as Partial<M["$inferInsert"]>,
          tx
        );

        if (result.length === 0) {
          return res
            .status(404)
            .send({ error: `No ${this.esService.index} found.` });
        }

        await this.esService.update(id, updateData);

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
      await this.pgService.transaction(async (tx) => {
        const result = await this.pgService.delete(id, tx);

        if (result.length === 0) {
          return res
            .status(404)
            .send({ error: `No ${this.esService.index} found.` });
        }

        await this.esService.delete(id);

        await this.onAfterDelete(id);
      });
      return res.status(200).send({ data: id });
    } catch (e) {
      return res.status(500).send({ error: `Delete failed: ${e}` });
    }
  }

  public formatPaginatedResponse(
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
