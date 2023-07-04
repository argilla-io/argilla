<template>
  <div>
    <base-spinner v-if="$fetchState.pending" />
    <documentation-viewer
      class="help-info__content"
      v-else
      :content="content"
    />
  </div>
</template>

<script>
export default {
  data() {
    return {
      content: {
        tabs: [],
      },
    };
  },
  async fetch() {
    try {
      const folderContent = require.context(
        `../../../../docs/_source/_common/`,
        false,
        /^[^_]+\.md$/,
        "lazy"
      );

      const helpContent = await folderContent("./shortcuts.md");

      this.content.tabs.push({
        id: "shortcuts",
        name: "Shortcuts",
        html: helpContent.html,
      });
    } catch (e) {
      console.log(e);
    }
  },
};
</script>

<style lang="scss" scoped>
.help-info__content {
  min-width: 450px;
}
:deep(table) {
  width: 100%;
  border-collapse: collapse;
  border-radius: $border-radius;
  border-spacing: 0;
  box-shadow: 0 0.2rem 0.5rem rgba(0, 0, 0, 0.05),
    0 0 0.0625rem rgba(0, 0, 0, 0.1);
  td,
  th {
    border-bottom: 1px solid $black-4;
    border-left: 1px solid $black-4;
    border-right: 1px solid $black-4;
    padding: 0 0.25rem;
    height: $base-space * 5;
  }
  th {
    background: $black-4;
    border: none;
  }
  thead tr:last-child th:last-child {
    border-top-right-radius: $border-radius;
  }
  thead tr:first-child th:first-child {
    border-top-left-radius: $border-radius;
  }
  td:last-child,
  th:last-child {
    border-left: none;
    border-right: none;
  }
  td:first-child,
  th:first-child {
    border-left: none;
  }
  code {
    padding: calc($base-space / 2);
    border: 1px solid $black-10;
    border-radius: $border-radius;
    background: $black-4;
  }
}
</style>

</style>
