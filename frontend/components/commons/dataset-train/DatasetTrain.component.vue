<template>
  <div class="snippet__container">
    <base-tabs
      class="train__tabs"
      :tabs="snippetsTabs"
      :active-tab="visibleTab"
      @change-tab="getSelectedLibrary"
    />
    <transition v-if="snippet" name="fade" mode="out-in" appear>
      <div class="snippet" :key="visibleTab.id">
        <h1 v-if="snippetAttributes.title" class="snippet__title --heading5">
          {{ snippetAttributes.title }}
        </h1>
        <h2
          v-if="snippetAttributes.description"
          class="snippet__description --body2"
        >
          {{ snippetAttributes.description }}
        </h2>
        <!-- <div class="snippet__code" v-if="snippet.html">
          <div v-highlight v-html="snippet.html"></div>
          <base-action-tooltip tooltip="Copied">
            <base-button
              class="secondary small"
              @on-click="copyCode(snippet.html)"
            >
              <svgicon name="copy" width="16" height="16" />
              Copy
            </base-button>
          </base-action-tooltip>
        </div> -->
        <base-code
          v-if="snippet.html"
          :code="parseHtml(snippet.html)"
        ></base-code>
        <base-button
          v-if="snippetAttributes.buttonLink"
          class="snippet__button primary small text"
          :href="snippetAttributes.buttonLink"
          target="_blank"
          >{{ snippetAttributes.buttonText }}</base-button
        >
      </div>
    </transition>
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
    };
  },
  computed: {
    snippetsTabs() {
      return [
        this.getLibrary("Transformers"),
        ...((this.datasetTask !== "Text2Text" && [this.getLibrary("Spacy")]) ||
          []),
        ...((this.datasetTask === "TextClassification" && [
          this.getLibrary("Setfit"),
        ]) ||
          []),
        this.getLibrary("Spark-nlp"),
        this.getLibrary("AutoTrain"),
      ];
    },
    task() {
      switch (this.datasetTask) {
        case "TextClassification":
          return "text-classification";
        case "TokenClassification":
          return "token-classification";
        case "Text2Text":
          return "text-generation";
      }
    },
    visibleTab() {
      return this.selectedComponent || this.snippetsTabs[0];
    },
    snippet() {
      try {
        return require(`../../../../docs/_source/_common/snippets/training/${this.task}/${this.visibleTab.id}.md`);
      } catch {
        return null;
      }
    },
    snippetAttributes() {
      return this.snippet?.attributes;
    },
  },
  methods: {
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
        id: name.toLowerCase(),
        name,
      };
    },
  },
};
</script>

<style lang="scss" scoped>
.snippet {
  margin-top: $base-space * 3;
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
  &__button {
    display: inline-flex;
  }
}
</style>