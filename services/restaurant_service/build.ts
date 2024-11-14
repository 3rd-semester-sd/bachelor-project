import path from "node:path";
import { cp } from "node:fs/promises";
import { build } from "esbuild";
import type { Plugin } from "esbuild";
import { copy } from "esbuild-plugin-copy";
import esbuildPluginPino from "esbuild-plugin-pino";
import glob from "tiny-glob";


(async function () {
  // Get all ts files
  const entryPoints = await glob("src/**/*.ts");

  build({
    entryPoints,
    logLevel: "info",
    outdir: "dist",
    bundle: true,
    minify: true,
    platform: "node",
    format: "cjs",
    sourcemap: true,
    plugins: [
      esbuildPluginPino({ transports: ["pino-pretty"] }),
      copy({
        resolveFrom: "cwd",
        assets: {
          from: ["node_modules/@fastify/swagger-ui/static/*"],
          to: ["dist/static"],
        },
      }),
    ],
  });
})();
