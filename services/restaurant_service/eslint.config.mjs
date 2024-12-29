import globals from "globals";
import pluginJs from "@eslint/js";
import tseslintPlugin from "@typescript-eslint/eslint-plugin";
import tsParser from "@typescript-eslint/parser";
import unusedImports from "eslint-plugin-unused-imports";

export default [
  {
    files: ["**/*.{js,mjs,cjs,ts}"],
    languageOptions: {
      parser: tsParser,
      globals: globals.browser,
    },
    plugins: {
      "@typescript-eslint": tseslintPlugin,
      "unused-imports": unusedImports,
    },
    rules: {
      // ESLint recommended rules
      ...pluginJs.configs.recommended.rules,

      // TypeScript recommended rules
      ...tseslintPlugin.configs.recommended.rules,

      // Custom rules for unused imports
      "@typescript-eslint/no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
      "unused-imports/no-unused-imports": "error", // Automatically remove unused imports
      "unused-imports/no-unused-vars": [
        "error",
        {
          vars: "all",
          varsIgnorePattern: "^_",
          args: "after-used",
          argsIgnorePattern: "^_",
        },
      ],
    },
  },
];
