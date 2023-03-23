<template>
  <div>
    <base-tabs
      class="train__tabs"
      :tabs="snippets"
      :active-tab="visibleTab"
      @change-tab="getSelectedHelpComponent"
    />
    <template v-if="currentSnippet">
      <transition name="fade" mode="out-in" appear>
        <div v-highlight v-html="currentSnippet.html"></div>
        <base-code :code="currentSnippet.html"></base-code>
      </transition>
    </template>
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
    snippets() {
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
      return this.selectedComponent || this.snippets[0];
    },
    currentSnippet() {
      return require(`../../../../docs/_source/_common/snippets/training/TextClassification/${this.visibleTab.id}.md`);
    },
  },
  methods: {
    getSelectedHelpComponent(id) {
      this.selectedComponent = this.snippets.find(
        (snippet) => snippet.id === id
      );
    },
  },
};
</script>