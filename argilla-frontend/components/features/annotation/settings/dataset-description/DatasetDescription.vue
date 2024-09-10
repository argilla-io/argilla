<template>
  <div class="description">
    <h2
      class="--heading5 --medium description__title"
      v-text="$t('annotationGuidelines')"
    />
    <BaseCardWithTabs :tabs="tabs">
      <template v-slot="{ currentComponent }">
        <component
          class="description__content"
          :markdown="sanitizedDescription"
          :value="sanitizedDescription"
          :originalValue="originalSanitizedDescription"
          :is="currentComponent"
          :key="currentComponent"
          @change-text="onChangeTextArea"
        />
      </template>
    </BaseCardWithTabs>
  </div>
</template>

<script>
export default {
  props: {
    dataset: {
      type: Object,
    },
  },
  model: {
    prop: "dataset",
  },
  data() {
    return {
      tabs: [
        {
          id: "0",
          name: this.$t("write"),
          component: "ContentEditableFeedbackTask",
        },
        {
          id: "1",
          name: this.$t("preview"),
          component: "RenderMarkdownBaseComponent",
        },
      ],
    };
  },
  computed: {
    sanitizedDescription() {
      return this.dataset.guidelines ?? "";
    },
    originalSanitizedDescription() {
      return this.dataset.original.guidelines ?? "";
    },
  },
  methods: {
    onChangeTextArea(newText) {
      this.dataset.guidelines = newText;
    },
  },
};
</script>

<style lang="scss" scoped>
.description {
  &__content {
    min-height: 65px;
    display: block;
    background: var(--bg-accent-grey-1);
    padding: $base-space;
    border-radius: $border-radius;
    border: 1px solid var(--bg-opacity-10);
    &:focus-within {
      border-color: var(--fg-cuaternary);
    }

    :deep(.content__text) {
      padding: unset !important;
    }
  }
}
</style>
