<template>
  <div class="train">
    <div
      v-if="!$fetchState.pending && !$fetchState.error"
      class="snippet__container"
    >
      <base-tabs
        class="train__tabs"
        :tabs="snippetsTabs"
        :active-tab="visibleTab"
        @change-tab="getSelectedLibrary"
      />
      <transition v-if="snippet" name="fade" mode="out-in" appear>
        {{ visibleTab }}
        <div class="snippet" :key="visibleTab.id" v-if="visibleTab">
          <h1 v-if="snippetAttributes.title" class="snippet__title --heading5">
            {{ snippetAttributes.title }}
          </h1>
          <h2
            v-if="snippetAttributes.description"
            class="snippet__description --body2"
          >
            {{ snippetAttributes.description }}
          </h2>
          <base-code
            v-if="snippet.html"
            :code="parseHtml(snippet.html)"
          ></base-code>
          <div class="library__buttons" v-if="snippetAttributes.links">
            <base-button
              v-for="(button, index) in snippetAttributes.links"
              :key="index"
              class="library__button primary small text"
              :href="button.linkLink"
              target="_blank"
              >{{ button.linkText }}</base-button
            >
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    datasetTask: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      selectedComponent: null,
      currentTaskLibraries: [],
    };
  },
  async fetch() {
    const libraries = require.context(
      `../../../../docs/_source/_common/snippets/training`,
      true,
      /^[^_]+\.md$/,
      "lazy"
    );
    this.getCurrentTaskLibraries(libraries).forEach(async (library) => {
      const newLib = await libraries(library);
      this.currentTaskLibraries.push(newLib);
    });
  },
  computed: {
    snippetsTabs() {
      return this.currentTaskLibraries.map((library) => {
        return this.getLibrary(library?.attributes?.title);
      });
    },
    task() {
      switch (this.datasetTask) {
        case "TextClassification":
          return "text-classification";
        case "TokenClassification":
          return "token-classification";
        case "Text2Text":
          return "text2text";
      }
    },
    snippet() {
      return (
        this.currentTaskLibraries.find(
          (library) => library.attributes.title === this.visibleTab.name
        ) || {}
      );
    },
    visibleTab() {
      return this.selectedComponent || this.snippetsTabs[0];
    },
    snippetAttributes() {
      return this.snippet?.attributes;
    },
  },
  methods: {
    getCurrentTaskLibraries(libraries) {
      return libraries.keys().filter((library) => library.includes(this.task));
    },
    getSelectedLibrary(id) {
      this.selectedComponent = this.snippetsTabs.find(
        (snippet) => snippet.id === id
      );
    },
    parseHtml(snippet) {
      const snippetCode = new DOMParser().parseFromString(snippet, "text/html");
      return snippetCode.body.textContent;
    },
    copyCode(snippet) {
      this.$copyToClipboard(this.parseHtml(snippet));
    },
    getLibrary(name) {
      return {
        id: name.trim().toLowerCase(),
        name,
      };
    },
  },
};
</script>

<style lang="scss" scoped>
.train {
  min-width: 800px;
  &__tabs.tabs {
    margin: 0 -2.5em 2em;
    padding: 0 2.5em;
  }
}
.snippet {
  margin: 0 -2.5em;
  padding: 0 2.5em;
  max-height: calc(100vh - 240px);
  overflow: auto;
  @extend %hide-scrollbar;
  :deep(code) {
    border-radius: $border-radius;
  }
  &__container {
    width: 800px;
  }
  &__code {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  &__description {
    font-weight: normal;
  }
}
.library {
  &__buttons {
    display: flex;
    flex-direction: column;
    gap: $base-space;
  }
  &__button {
    display: inline-flex;
  }
}
</style>