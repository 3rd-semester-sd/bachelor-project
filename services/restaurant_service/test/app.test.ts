import { app } from "../src/app";

describe("App", () => {
  beforeAll(async () => {
    try {
      await app.ready();
    } catch (err) {
      console.error("Error during app.ready():", err);
      throw err;
    }
  });

  afterAll(async () => {
    await app.close();
  });

  it("should be defined", () => {
    expect(app).toBeDefined();
  });

  it("should have swagger docs", async () => {
    const response = await app.inject({
      method: "GET",
      url: "/docs",
    });
    expect(response.statusCode).toBe(200);
  });
});
