<template>
  <div class="datasets-empty">
    <base-spinner v-if="$fetchState.pending" />
    <documentation-viewer
      class="datasets-empty__content"
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
    const folderContent = require.context(
      `../../../../../../docs/_source/_common/snippets`,
      false,
      /.start_page.md/,
      "lazy"
    );

    const startPage = await folderContent("./start_page.md");

    this.content.tabs.push({
      id: "start-page",
      name: "Start page",
      markdown: startPage.body,
    });
  },
};
</script>
<style lang="scss" scoped>
.datasets-empty {
  &__content {
    max-width: max(900px, 50vw);
    width: auto;
    padding-top: $base-space * 2;
    padding-bottom: $base-space * 4;
    color: $black-54;
    line-height: 1.5;
  }
  :deep(h1),
  :deep(h2),
  :deep(h3),
  :deep(h4) {
    color: $black-87;
  }
}
:deep(.start-page__intro) {
  margin-bottom: $base-space * 3;
  text-align: center;
  h1 {
    display: block;
    @include font-size(20px);
    font-family: "raptor_v2_premiumbold", "Helvetica", "Arial", sans-serif;
    margin-top: 30px;
    font-weight: lighter;
    &:after {
      content: "";
      display: block;
      height: min(30px, 30vw);
      background: url("/images/logo.svg") center / contain no-repeat;
      margin: $base-space * 2;
    }
  }
  h2 {
    font-weight: 500;
    @include font-size(16px);
  }
}
:deep(.start-page__content) {
  display: inline-block;
  background: palette(white);
  padding: $base-space * 3;
  border: 1px solid $black-10;
  border-radius: $border-radius-m;
  p,
  li {
    @include font-size(16px);
    margin-bottom: 8px;
  }
  h3 {
    display: block;
    margin-top: 30px;
  }
  a {
    text-decoration: none;
    color: $primary-color;
    &:hover {
      color: darken($primary-color, 10%);
    }
  }
  p > code:not(.hljs),
  li > code:not(.hljs) {
    color: $black-54;
    border: 1px solid $black-10;
    background: $black-4;
    padding-inline: 4px;
    @include font-size(14px);
  }
}
</style>
