import globals from "globals";
import pluginJs from "@eslint/js";
import tseslint from "typescript-eslint";

/** @type {import('eslint').Linter.Config[]} */
export default [
  { files: ["**/*.{js,mjs,cjs,ts}"] },
  { languageOptions: { globals: globals.browser } },
  {
    rules: {
      eqeqeq: "off",
      "no-unused-vars": "error",
      "prefer-const": ["error", { ignoreReadBeforeAssign: true }],
      "quotes": ["error", "double"],  // Enforce double quotes
      "semi": ["error", "always"],    // Require semicolons
      "no-console": "warn",           // Warn on console.log usage
      "indent": ["error", 2],         // Enforce consistent indentation (2 spaces)
      
    },
  },
  pluginJs.configs.recommended,
  ...tseslint.configs.recommended,
];
