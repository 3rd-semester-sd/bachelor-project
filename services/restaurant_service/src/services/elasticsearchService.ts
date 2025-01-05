import { FastifyInstance } from "fastify";

export class ElasticsearchService<T> {
  constructor(
    private fastify: FastifyInstance,
    public index: string
  ) {}

  async search(query: any, offset?: number, size?: number) {
    const esResult = await this.fastify.elastic.search<T>({
      index: this.index,
      query,
      ...(offset !== undefined && { from: offset }),
      ...(size !== undefined && { size }),
    });
    return esResult;
  }

  async getById(id: string) {
    return this.search({ match: { _id: id } });
  }

  async create(id: string, document: any) {
    return await this.fastify.elastic.index({
      index: this.index,
      id,
      document,
    });
  }

  async update(id: string, document: any) {
    return await this.fastify.elastic.update({
      index: this.index,
      id,
      doc: document,
    });
  }

  async delete(id: string) {
    return await this.fastify.elastic.delete({
      index: this.index,
      id,
    });
  }
}
