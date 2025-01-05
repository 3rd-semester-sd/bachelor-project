import { AnyPgTable, PgTransaction } from "drizzle-orm/pg-core";
import { eq } from "drizzle-orm";
import { FastifyInstance } from "fastify";

export class PostgresService<M extends AnyPgTable> {
  constructor(
    private fastify: FastifyInstance,
    public table: M,
    public idField: string
  ) {}

  async create(data: M["$inferInsert"], tx?: PgTransaction<any, any, any>) {
    const queryBuilder = tx || this.fastify.db;
    const inserted = await queryBuilder
      .insert(this.table)
      .values(data)
      .returning({
        [this.idField]: (this.table as unknown as Record<string, any>)[
          this.idField
        ],
      });
    console.log(inserted);
    return inserted[0];
  }

  async update(
    id: string,
    data: Partial<M["$inferInsert"]>,
    tx?: PgTransaction<any, any, any>
  ) {
    const queryBuilder = tx || this.fastify.db;
    return await queryBuilder
      .update(this.table)
      .set(data)
      .where(
        eq((this.table as unknown as Record<string, any>)[this.idField], id)
      )
      .returning();
  }

  async delete(id: string, tx?: PgTransaction<any, any, any>) {
    const queryBuilder = tx || this.fastify.db;
    return await queryBuilder
      .delete(this.table)
      .where(
        eq((this.table as unknown as Record<string, any>)[this.idField], id)
      )
      .returning();
  }

  async transaction<T>(
    callback: (tx: PgTransaction<any, any, any>) => Promise<T>
  ): Promise<T> {
    return await this.fastify.db.transaction(callback);
  }
}
