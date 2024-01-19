/*
 * coding=utf-8
 * Copyright 2021-present, the Recognai S.L. team.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

module.exports = {
  root: true,
  env: {
    node: true,
    browser: true,
    jest: true,
  },
  extends: [
    "eslint:recommended",
    "plugin:@intlify/vue-i18n/recommended",
    "plugin:prettier/recommended",
    "plugin:nuxt/recommended",
    "prettier/vue",
  ],
  settings: {
    "vue-i18n": {
      localeDir: "./translation/*.json",
    },
  },
  rules: {
    "no-console": process.env.NODE_ENV === "production" ? "error" : "off",
    "no-debugger": process.env.NODE_ENV === "production" ? "error" : "off",
    "prefer-const": "error",
    "prefer-arrow-callback": "error",
    "no-unused-vars": ["error", { ignoreRestSiblings: true }],
    "@intlify/vue-i18n/no-raw-text": "off",
    "@intlify/vue-i18n/no-v-html": "off",
    "@intlify/vue-i18n/no-missing-keys": "error",
  },
  globals: {
    $nuxt: true,
  },
  parserOptions: {
    parser: "@babel/eslint-parser",
  },
  overrides: [
    {
      files: ["**/*.ts"],
      extends: ["@nuxtjs/eslint-config-typescript", "prettier"],
      parser: "@typescript-eslint/parser",
      plugins: ["@typescript-eslint", "prettier"],
      parserOptions: { project: ["./tsconfig.json"] },
      rules: {
        "prettier/prettier": ["error"],
        quotes: ["error", "double"],
        semi: ["error", "always"],
        "import/no-named-as-default-member": 0,
        "no-useless-constructor": 0,
        "space-before-function-paren": 0,
        "no-throw-literal": 0,
        "no-new": 0,
      },
    },
  ],
};
