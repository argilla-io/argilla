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

import { NuxtConfig } from "@nuxt/types";
import Mode from "frontmatter-markdown-loader/mode";
import pkg from "./package.json";

const LOCAL_ENVIRONMENT = "http://localhost:6900";
const BASE_URL = process.env.API_BASE_URL ?? LOCAL_ENVIRONMENT;
const DIST_FOLDER = process.env.DIST_FOLDER || "dist";

const config: NuxtConfig = {
  // Disable server-side rendering (https://go.nuxtjs.dev/ssr-mode)
  ssr: false,
  telemetry: false,
  generate: {
    dir: DIST_FOLDER,
  },

  // Global page headers (https://go.nuxtjs.dev/config-head)
  head: {
    title: "Argilla",
    meta: [
      { charset: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { hid: "description", name: "description", content: "" },
    ],
    link: [
      { rel: "icon", type: "image/x-icon", href: "favicon.ico" },
      {
        rel: "apple-touch-icon",
        sizes: "180x180",
        href: "apple-touch-icon.png",
      },
      { rel: "icon", sizes: "32x32", href: "favicon-32x32.png" },
      { rel: "icon", sizes: "16x16", href: "favicon-16x16.png" },
      { rel: "manifest", href: "site.webmanifest" },
    ],
  },

  // Global CSS (https://go.nuxtjs.dev/config-css)
  css: ["~assets/scss/base/base.scss"],

  // Plugins to run before rendering page (https://go.nuxtjs.dev/config-plugins)
  plugins: [
    { src: "~/plugins/logo" },

    { src: "~/plugins/directives" },

    { src: "~/plugins/di" },

    { src: "~/plugins/language" },

    { src: "~/plugins/plugins/axios.ts" },
    { src: "~/plugins/plugins/axios-cache.ts" },
    { src: "~/plugins/plugins/svg-icon.js" },
    { src: "~/plugins/plugins/click-outside.js" },
    { src: "~/plugins/plugins/toast.ts" },
    { src: "~/plugins/plugins/copy-to-clipboard.js" },
    { src: "~/plugins/plugins/filters.js" },
    { src: "~/plugins/plugins/vue-draggable.js" },
    { src: "~/plugins/plugins/platform.ts" },
    { src: "~/plugins/plugins/language.ts" },
  ],

  // Auto import components (https://go.nuxtjs.dev/config-components)
  components: [
    {
      path: "~/components",
      pattern: "**/*.vue",
      pathPrefix: false,
      level: 1,
    },
  ],

  // Modules for dev and build (recommended) (https://go.nuxtjs.dev/config-modules)
  buildModules: [
    // https://go.nuxtjs.dev/typescript
    "@nuxt/typescript-build",
    "@nuxtjs/composition-api/module",
    ["@pinia/nuxt", { disableVuex: false }],
  ],

  // Modules (https://go.nuxtjs.dev/config-modules)
  modules: [
    "@nuxtjs/style-resources",
    "@nuxtjs/axios",
    "@nuxtjs/auth-next",
    "nuxt-highlightjs",
    "@nuxtjs/i18n",
  ],

  i18n: {
    locales: [
      {
        code: "en",
        file: "en.js",
      },
      {
        code: "de",
        file: "de.js",
      },
    ],
    detectBrowserLanguage: false,
    vueI18n: {
      fallbackLocale: "en",
    },
    lazy: true,
    langDir: "translation/",
    defaultLocale: "en",
    strategy: "no_prefix",
  },

  // Axios module configuration (https://go.nuxtjs.dev/config-axios)
  axios: {
    proxy: true,
    browserBaseURL: "api",
  },

  proxy: {
    "/api/": {
      target: BASE_URL,
    },
  },

  // Build Configuration (https://go.nuxtjs.dev/config-build)
  build: {
    cssSourceMap: false,
    extend(config) {
      config.resolve.alias.vue = "vue/dist/vue.common";
      config.module.rules.push({
        test: /\.md$/,
        loader: "frontmatter-markdown-loader",
        options: {
          mode: [Mode.BODY],
        },
      });
    },
    babel: {
      plugins: [["@babel/plugin-proposal-private-methods", { loose: true }]],
    },
    terser: {
      terserOptions: {
        keep_classnames: true,
        keep_fnames: true,
      },
    },
  },

  // https://github.com/nuxt-community/style-resources-module
  styleResources: {
    scss: "./assets/scss/abstract.scss",
  },

  loading: false,

  auth: {
    strategies: {
      basic: {
        scheme: "local",
        token: {
          property: "access_token",
        },
        user: {
          property: false,
          autoFetch: true,
        },
        endpoints: {
          login: {
            url: "/v1/token",
            method: "post",
            propertyName: "access_token",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
          },
          logout: false,
          user: { url: "/v1/me", propertyName: false },
        },
      },
    },
    cookie: false,
    resetOnError: true,
    redirect: { login: "/sign-in", logout: "/sign-in" },
  },

  router: {
    middleware: ["auth-guard"],
    base: process.env.BASE_URL ?? "/",
  },

  publicRuntimeConfig: {
    clientVersion: pkg.version,
    slackCommunity:
      "https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g",
    documentationSite: "https://docs.argilla.io/",
    documentationSiteQuickStart:
      "https://docs.argilla.io/en/latest/getting_started/quickstart.html",
    documentationSiteSemanticSearch:
      "https://docs.argilla.io/en/latest/reference/webapp/features.html#semantic-search",
    documentationSiteLabelScheme:
      "https://docs.argilla.io/en/latest/guides/log_load_and_prepare_data.html#define-a-labeling-schema",
    documentationSiteQueryDatasets:
      "https://docs.argilla.io/en/latest/guides/query_datasets.html",
    documentationPersistentStorage:
      "https://docs.argilla.io/en/latest/getting_started/installation/deployments/huggingface-spaces.html#setting-up-persistent-storage",
  },
};
export default config;
