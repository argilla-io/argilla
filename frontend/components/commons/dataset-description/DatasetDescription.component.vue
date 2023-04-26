<template>
  <div class="description">
    <h2 class="--heading5 --semibold description__title">{{ title }}</h2>
    <p class="--body1 description__text" v-text="datasetDescription" />
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
  created() {
    this.title = "Description and annotation guidelines";
  },
};
</script>

<style lang="scss" scoped>
.description {
  &__text {
    color: $black-37;
    &:first-letter {
      text-transform: capitalize;
    }
  }
}
</style>
