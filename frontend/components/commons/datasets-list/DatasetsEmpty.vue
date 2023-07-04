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

    const docElement = new DOMParser().parseFromString(
      startPage.html,
      "text/html"
    ).documentElement;

    const codeBlocks = docElement.getElementsByTagName("pre");

    for (const codeBlock of codeBlocks) {
      const tabName = codeBlock.previousElementSibling.innerText.replace(
        ":::{tab-item} ",
        ""
      );
      const code = codeBlock.innerText;

      this.content.tabs.push({
        id: tabName.trim().toLowerCase(),
        name: tabName,
        html: `<base-code code='${code}'></base-code>`,
      });
    }
  },
};
</script>
<style lang="scss" scoped>
.datasets-empty {
  display: flex;
  flex-direction: column;
  justify-content: start;
  align-items: center;
  text-align: center;
  color: $black-54;
  line-height: 20px;
  margin-top: 3em;
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
