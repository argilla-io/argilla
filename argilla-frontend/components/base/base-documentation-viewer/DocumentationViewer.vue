<template>
  <div class="snippet__container">
    <BaseTabs
      v-if="content.tabs.length > 1"
      class="snippets__tabs"
      :tabs="content.tabs"
      :active-tab="currentTab"
      @change-tab="onChangeTab"
    />
    <transition v-if="currentTab" name="fade" mode="out-in" appear>
      {{ currentTab }}
      <div class="snippet" :key="currentTab.id" v-if="currentTab">
        <h1 v-if="currentTab.title" class="snippet__title --heading5">
          {{ currentTab.title }}
        </h1>
        <h2 v-if="currentTab.description" class="snippet__description --body2">
          {{ currentTab.description }}
        </h2>
        <MarkdownRenderer
          v-if="currentTab.markdown"
          :markdown="currentTab.markdown"
        />
        <div class="library__buttons" v-if="currentTab.links">
          <p class="library__section__title">Links</p>
          <BaseButton
            v-for="(button, index) in currentTab.links"
            :key="index"
            class="library__button primary small text"
            :href="button.linkLink"
            target="_blank"
            >{{ button.linkText }}</BaseButton
          >
        </div>
      </div>
    </transition>
  </div>
</template>
<script>
export default {
  props: {
    content: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      currentTab: this.content.tabs[0],
    };
  },
  methods: {
    onChangeTab(tabId) {
      this.currentTab = this.content.tabs.find((tab) => tab.id === tabId);
    },
  },
};
</script>

<style lang="scss" scoped>
.snippets {
  &__tabs.tabs {
    margin: 0 -2.5em 2em;
    padding: 0 2.5em;
  }
}

.snippet {
  margin: 0 -2.5em;
  padding: 0 2.5em;
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
    color: var(--fg-secondary);
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
      color: var(--fg-secondary);
      font-weight: 600;
      @include font-size(15px);
    }
  }
}
</style>
