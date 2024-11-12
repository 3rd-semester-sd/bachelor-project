import type { Plugin } from "esbuild";
import { build } from "esbuild";
import { cp } from "node:fs/promises";
import path from "node:path";
import glob from "tiny-glob";

const OUTDIR = "dist";

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
  });
})();
