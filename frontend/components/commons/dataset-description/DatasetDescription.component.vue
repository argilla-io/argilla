<template>
  <div class="description">
    <h2 class="--heading5 --semibold description__title">{{ title }}</h2>
    <p class="--body2 description__text">{{ datasetDescription }}</p>
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
  data: () => {
    return {
      title: "Description and annotation guidelines",
    };
  },
};
</script>

<style lang="scss" scoped>
.description {
  &__text {
    color: $black-37;
  }
}
</style>
