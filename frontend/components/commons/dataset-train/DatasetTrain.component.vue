<template>
  <div>
    <base-spinner v-if="$fetchState.pending" />
    <documentation-viewer v-else :content="content" />
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
        html: this.parseHTML(library.html),
        ...library.attributes,
      });
    }
  },
  methods: {
    parseHTML(code) {
      const docElement = new DOMParser().parseFromString(
        code,
        "text/html"
      ).documentElement;
      const preBlocks = docElement.getElementsByTagName("pre");

      for (let i = 0; i < preBlocks.length; i++) {
        const code = preBlocks[i].innerText;
        preBlocks[i].innerHTML = `<base-code code='${code}'></base-code>`;
      }

      const html = docElement.getElementsByTagName("body")[0].innerHTML;
      const htmlWithVariables = html
        .replace("<my_dataset_name>", this.datasetName)
        .replace("<my_workspace_name>", this.workspaceName);

      return `<div>${htmlWithVariables}</div>`;
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
.training-snippets {
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
    margin-bottom: $base-space * 2;
  }
  :deep(em) {
    color: $black-54;
  }
}
.library {
  &__buttons {
    display: flex;
    flex-direction: column;
    gap: $base-space;
    margin-top: $base-space * 3;
  }
  &__button {
    display: inline-flex;
    padding: 0;
    @include line-height(16px);
  }
  &__section {
    &__title {
      margin-bottom: $base-space;
      color: $black-54;
      font-weight: 600;
      @include font-size(15px);
    }
  }
}
</style>
