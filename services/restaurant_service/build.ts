import type { Plugin } from "esbuild";
import { build } from "esbuild";
import esbuildPluginPino from "esbuild-plugin-pino";
import { cp } from "node:fs/promises";
import path from "node:path";
import glob from "tiny-glob";
import { copy } from "esbuild-plugin-copy";
const OUTDIR = "dist";


(async function () {
  // Get all ts files
  const entryPoints = await glob("src/**/**.ts");

  build({
    entryPoints,
    logLevel: "info",
    outdir: OUTDIR,
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
          to: ["dist/static", "dist/docs/static"],
        },
      }),
    ],
  });
})();
