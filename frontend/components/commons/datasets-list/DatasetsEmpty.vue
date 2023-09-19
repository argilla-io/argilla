<template>
  <div class="datasets-empty">
    <div class="datasets-empty__body">
      <svgicon
        class="datasets-empty__icon"
        width="44"
        height="46"
        name="unavailable"
      />
      <p class="datasets-empty__title">There aren't any datasets yet</p>
      <p class="datasets-empty__subtitle">
        The Argilla web app allows you to log, explore and annotate your
        data.<br />
        Start logging data with our Python client, or
        <a :href="$config.documentationSite" target="_blank">see the docs</a>
        for more information.
      </p>
    </div>
    <base-spinner v-if="$fetchState.pending" />
    <documentation-viewer v-else :content="content" />
  </div>
</template>

<script>
import "assets/icons/unavailable";
const TAB_MARKER = ":::{tab-item} ";
const TAB_ITEM_FINISH_MARKER = ":::";
const TAB_FINISH_MARKER = "::::";

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
      `../../../../docs/_source/_common/snippets`,
      false,
      /.start_page.md/,
      "lazy"
    );

    const startPage = await folderContent("./start_page.md");

    const tabs = startPage.body.split(TAB_MARKER);
    tabs.shift();

    for (const tab of tabs) {
      const tabName = tab.split("\n")[0].trim();

      const code = tab
        .replace(tabName, "")
        .replace(TAB_ITEM_FINISH_MARKER, "")
        .replace(TAB_FINISH_MARKER, "")
        .trim();

      this.content.tabs.push({
        id: tabName.trim().toLowerCase(),
        name: tabName,
        markdown: code,
      });
    }
  },
};
</script>
<style lang="scss" scoped>
.datasets-empty {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  text-align: center;
  color: $black-54;
  line-height: 20px;
  padding-top: 3vh;
  &__body {
    height: fit-content;
  }
  &__icon {
    margin-bottom: 1em;
  }
  &__title {
    margin: 0 auto 1em auto;
    @include font-size(20px);
    font-weight: 300;
    max-width: 520px;
  }
  &__subtitle {
    margin: 0 auto 1em auto;
    @include font-size(14px);
    max-width: 520px;
    a {
      color: $brand-primary-color;
      text-decoration: none;
      &:hover {
        color: darken($brand-primary-color, 10%);
      }
    }
  }
}
</style>
