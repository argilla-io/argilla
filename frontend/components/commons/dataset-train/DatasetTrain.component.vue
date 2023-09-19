<template>
  <div>
    <base-spinner v-if="$fetchState.pending" />
    <documentation-viewer class="dataset-training" v-else :content="content" />
  </div>
</template>

<script>
export default {
  props: {
    datasetTask: {
      type: String,
      required: true,
    },
    workspaceName: {
      type: String,
      required: true,
    },
    datasetName: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      content: {
        tabs: [],
      },
    };
  },
  async fetch() {
    const libraries = await this.getLibraries();

    for (const library of libraries) {
      this.content.tabs.push({
        id: library.attributes.title.trim().toLowerCase(),
        name: library.attributes.title,
        markdown: this.replaceValues(library.body),
        ...library.attributes,
      });
    }
  },
  methods: {
    replaceValues(markdown) {
      return markdown
        .replace("<my_dataset_name>", this.datasetName)
        .replace("<my_workspace_name>", this.workspaceName);
    },
    getLibraries() {
      const getCurrentTaskLibraries = (libraries, task) => {
        return (
          libraries?.keys().filter((library) => library.includes(task)) ?? []
        );
      };

      const tasks = {
        TextClassification: "text-classification",
        TokenClassification: "token-classification",
        Text2Text: "text2text",
        FeedbackTask: "feedback-task",
      };

      try {
        const libraries = require.context(
          `../../../../docs/_source/_common/snippets/training`,
          true,
          /^[^_]+\.md$/,
          "lazy"
        );

        return Promise.all(
          getCurrentTaskLibraries(libraries, tasks[this.datasetTask]).map(
            (library) => libraries(library)
          )
        );
      } catch (e) {
        console.log(e);
      }

      return [];
    },
  },
};
</script>

<style lang="scss" scoped>
.dataset-training {
  min-width: 800px;
}
:deep(.snippet) {
  max-height: calc(100vh - 240px);
  overflow: auto;
}
</style>
