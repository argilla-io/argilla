require("dotenv").config();
const API_BASE_URL =
  process.env.API_BASE_URL || process.env.BASE_URL || "http://localhost:6900";

const DIST_FOLDER = process.env.DIST_FOLDER || "dist";

export default {
  // Disable server-side rendering (https://go.nuxtjs.dev/ssr-mode)
  ssr: false,

  generate: {
    dir: DIST_FOLDER,
  },

  // Global page headers (https://go.nuxtjs.dev/config-head)
  head: {
    title: "Rubrix",
    meta: [
      { charset: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { hid: "description", name: "description", content: "" },
    ],
    link: [{ rel: "icon", type: "image/x-icon", href: "/favicon.ico" }],
  },

  // Global CSS (https://go.nuxtjs.dev/config-css)
  css: ["~assets/scss/base/base.scss"],

  // Plugins to run before rendering page (https://go.nuxtjs.dev/config-plugins)
  plugins: [
    { src: "~/plugins/vuex-orm-axios.js" },
    { src: "~/plugins/moment.js" },
    { src: "~/plugins/svgicon.js" },
    { src: "~/plugins/vue-vega.js" },
    { src: "~/plugins/click-outside.js" },
    { src: "~/plugins/mock.js" },
    { src: "~/plugins/virtualScroller.js" },
    { src: "~/plugins/toast.js" },
    { src: "~/plugins/highlight-search.js" },
  ],

  // Auto import components (https://go.nuxtjs.dev/config-components)
  components: {
    dirs: [
      {
        path: "~/components",
        pattern: "**/*.vue",
        pathPrefix: false,
      },
    ],
  },

  // Modules for dev and build (recommended) (https://go.nuxtjs.dev/config-modules)
  buildModules: [],

  // Modules (https://go.nuxtjs.dev/config-modules)
  modules: ["@nuxtjs/style-resources", "@nuxtjs/axios", "@nuxtjs/dotenv"],

  // Axios module configuration (https://go.nuxtjs.dev/config-axios)
  axios: {
    proxy: true,
    browserBaseURL: "/api",
  },

  proxy: {
    "/api/": {
      target: API_BASE_URL,
      // pathRewrite: { "^/api/": "" },
    },
  },

  // Build Configuration (https://go.nuxtjs.dev/config-build)
  build: {
    cssSourceMap: false,
    extend(config) {
      config.resolve.alias["vue"] = "vue/dist/vue.common";
    },
  },

  // https://github.com/nuxt-community/style-resources-module
  styleResources: {
    scss: "./assets/scss/abstract.scss",
  },

  loading: { color: "#0508D9", throttle: 100 },
};
