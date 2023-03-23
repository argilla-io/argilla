<template>
  <div>
    <base-tabs
      class="train__tabs"
      :tabs="snippetsTabs"
      :active-tab="visibleTab"
      @change-tab="getSelectedHelpComponent"
    />
    <transition v-if="snippet" name="fade" mode="out-in" appear>
      <div class="snippet">
        <h1 v-if="snippetAttributes.title" class="snippet__title --heading3">
          {{ snippetAttributes.title }}
        </h1>
        <h2
          v-if="snippetAttributes.description"
          class="snippet__description --body2"
        >
          {{ snippetAttributes.description }}
        </h2>
        <base-code v-if="snippet.html" :code="snippet.html"></base-code>
        <base-button
          v-if="snippetAttributes.buttonLink"
          class="snippet__button primary"
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
      switch (this.datasetTask) {
        case "TextClassification":
          return [
            {
              id: "transformers",
              name: "Transformers",
            },
            {
              id: "spacy",
              name: "Spacy",
            },
            {
              id: "setfit",
              name: "Setfit",
            },
            {
              id: "spark-nlp",
              name: "Spark-nlp",
            },
            {
              id: "autotrain",
              name: "AutoTrain",
            },
          ];
        case "TokenClassification":
          return [
            {
              id: "transformers",
              name: "Transformers",
            },
            {
              id: "spacy",
              name: "Spacy",
            },
            {
              id: "spark-nlp",
              name: "Spark-nlp",
            },
            {
              id: "autotrain",
              name: "AutoTrain",
            },
          ];
        case "Text2Text":
          return [
            {
              id: "transformers",
              name: "Transformers",
            },
            {
              id: "spark-nlp",
              name: "Spark-nlp",
            },
            {
              id: "autotrain",
              name: "AutoTrain",
            },
          ];
        default:
          throw Error("unknown dataset task");
      }
    },
    visibleTab() {
      return this.selectedComponent || this.snippetsTabs[0];
    },
    snippet() {
      return require(`../../../../docs/_source/_common/snippets/training/TextClassification/${this.visibleTab.id}.md`);
    },
    snippetAttributes() {
      return this.snippet.attributes;
    },
  },
  methods: {
    getSelectedHelpComponent(id) {
      this.selectedComponent = this.snippetsTabs.find(
        (snippet) => snippet.id === id
      );
    },
  },
};
</script>

<style lang="scss" scoped>
.snippet {
  margin-top: $base-space * 5;
  max-width: 1000px;
  &__description {
    font-weight: normal;
  }
  &__button {
    display: inline-flex;
  }
}
</style>