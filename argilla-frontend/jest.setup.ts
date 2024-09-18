import Vue from "vue";
import { Nuxt, Builder } from "nuxt";
import SvgIcon from "vue-svgicon";
import { config } from "@vue/test-utils";
import nuxtConfig from "./nuxt.config";

const translationMock = (key, ...params) =>
  params.length
    ? `#${key}${params
        .map((l) => (Object.values(l).length ? Object.values(l) : l))
        .map((s) => `.${s}`)}#`
    : `#${key}#`;

jest.mock("~/v1/infrastructure/services/useTranslate", () => ({
  useTranslate: () => ({
    t: translationMock,
    tc: translationMock,
  }),
}));

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
  $t: translationMock,
  $language: {
    isRTL: () => false,
  },
};

export class IntersectionObserverMock {
  root = null;
  rootMargin = "";
  thresholds = [];

  disconnect() {
    return null;
  }

  observe() {
    return null;
  }

  takeRecords() {
    return [];
  }

  unobserve() {
    return null;
  }
}

window.IntersectionObserver = IntersectionObserverMock;
global.IntersectionObserver = IntersectionObserverMock;

export default async () => {
  const nuxt = await buildNuxt();

  process.env.buildDir = nuxt.options.buildDir;
};
