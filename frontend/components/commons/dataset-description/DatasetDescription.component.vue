<template>
  <div class="description">
    <h2 class="--heading5 --semibold description__title" v-text="title" />
    <RenderMarkdownBaseComponent
      class="--body1 description__text"
      :class="{ '--light': isColorLight }"
      :markdown="datasetDescription"
    />
  </div>
</template>

<script>
export default {
  props: {
    datasetDescription: {
      type: String,
      required: true,
    },
    isColorLight: {
      type: Boolean,
      default: false,
    },
  },
  created() {
    this.title = "Annotation guidelines";
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
    &.--light {
      color: $black-37;
    }
  }
}
</style>
