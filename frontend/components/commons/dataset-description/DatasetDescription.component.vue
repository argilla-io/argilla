<template>
  <div class="description">
    <h2
      class="--heading5 --semibold description__title"
      v-text="'Annotation guidelines'"
    />
    <BaseCardWithTabs :tabs="tabs">
      <template v-slot="{ currentComponent }">
        <component
          class="description__content"
          :markdown="datasetDescription"
          :value="datasetDescription"
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
    datasetDescription: {
      type: String,
      required: true,
    },
  },
  model: {
    prop: "datasetDescription",
    event: "input",
  },
  data() {
    return {
      tabs: [
        { name: "Raw", component: "ContentEditableFeedbackTask" },
        { name: "Preview", component: "RenderMarkdownBaseComponent" },
      ],
    };
  },
  methods: {
    onChangeTextArea(newText) {
      this.$emit("input", newText);
    },
  },
};
</script>

<style lang="scss" scoped>
.description {
  &__text {
    white-space: pre-wrap;
    color: $black-87;

    &:first-letter {
      text-transform: capitalize;
    }
  }
  &__content {
    display: block;
    background: palette(white);
    padding: $base-space * 2;
    border-radius: $border-radius;
    border: 1px solid $black-10;
    &:focus-within {
      border-color: $primary-color;
    }
  }
}
</style>
