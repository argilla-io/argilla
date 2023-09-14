<template>
  <div class="description">
    <h2
      class="--heading5 --medium description__title"
      v-text="'Annotation guidelines'"
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
        { name: "Write", component: "ContentEditableFeedbackTask" },
        { name: "Preview", component: "RenderMarkdownBaseComponent" },
      ],
    };
  },
  computed: {
    sanitizedDescription() {
      return this.dataset.guidelines ?? "";
    },
    originalSanitizedDescription() {
      return this.dataset.originalGuidelines ?? "";
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
    background: palette(white);
    padding: $base-space;
    border-radius: $border-radius;
    border: 1px solid $black-10;
    &:focus-within {
      border-color: $primary-color;
    }

    :deep(.content__text) {
      padding: unset !important;
    }
  }
}
</style>
