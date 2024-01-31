import Vue from "vue";
import { Nuxt, Builder } from "nuxt";
import SvgIcon from "vue-svgicon";
import { config } from "@vue/test-utils";
import nuxtConfig from "./nuxt.config";

Vue.use(SvgIcon);
Vue.directive("click-outside", {});
Vue.config.devtools = false;
Vue.config.productionTip = false;

const resetConfig = {
  loading: false,
  loadingIndicator: false,
  fetch: {
    client: false,
    server: false,
  },
  features: {
    store: true,
    layouts: false,
    meta: false,
    middleware: false,
    transitions: false,
    deprecations: false,
    validate: false,
    asyncData: false,
    fetch: false,
    clientOnline: false,
    clientPrefetch: false,
    clientUseUrl: false,
    componentAliases: false,
    componentClientOnly: false,
  },
  build: {
    indicator: false,
    terser: false,
  },
};

const overrideConfig = {
  ...nuxtConfig,
  ...resetConfig,
  mode: "spa",
  srcDir: nuxtConfig.srcDir,
  ignore: ["**/components/**/*", "**/layouts/**/*", "**/pages/**/*"],
};

const buildNuxt = async () => {
  const nuxt = new Nuxt(overrideConfig);
  await new Builder(nuxt).build();
  return nuxt;
};

config.mocks = {
  $t: (key) => `#${key}#`,
};

module.exports = async () => {
  const nuxt = await buildNuxt();

  process.env.buildDir = nuxt.options.buildDir;
};
