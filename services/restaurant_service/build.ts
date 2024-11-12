import type { Plugin } from "esbuild";
import { build } from "esbuild";
import { cp } from "node:fs/promises";
import path from "node:path";
import glob from "tiny-glob";

const OUTDIR = "dist";

/** esbuild plugin to copy static folder to outdir */
function esbuildPluginFastifySwaggerUi(): Plugin {
  return {
    name: "@fastify/swagger-ui",
    setup(build) {
      // const { outdir } = build.initialOptions;
      const outdir = path.join(__dirname, OUTDIR);
      const fastifySwaggerUi = path.dirname(
        require.resolve("@fastify/swagger-ui"),
      );
      const source = path.join(fastifySwaggerUi, "static");
      const dest = path.join(outdir, "static");

      build.onEnd(async () => cp(source, dest, { recursive: true }));
    },
  };
}

(async function () {
  // Get all ts files
  const entryPoints = await glob("src/main.ts");

  build({
    entryPoints,
    logLevel: "info",
    outdir: OUTDIR,
    bundle: true,
    minify: true,
    platform: "node",
    format: "cjs",
    sourcemap: true,
    plugins: [ esbuildPluginFastifySwaggerUi(),
    ],
  });
})();