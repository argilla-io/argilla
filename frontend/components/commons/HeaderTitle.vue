<template>
  <div class="filters__title">
    <h2 class="filters__title__info">{{ taskName }} records ({{ dataset.results.total }})
    </h2>
  </div>
</template>

<script>
export default {
  props: {
    dataset: {
      default: () => { },
      type: Object,
    },
  },
  computed: {
    taskName() {
      if (this.dataset.task === 'TokenClassification') {
        return 'Token Classification'
      } else if (this.dataset.task === 'TextClassification') {
        return 'Text Classification'
      }
    }
  }
};
</script>
<style lang="scss" scoped>
.filters {
  &__title {
    font-weight: normal;
    margin-right: auto;
    &__info {
      font-weight: normal;
      @include font-size(16px);
      color: $font-secondary-dark;
      white-space: nowrap;
      display: flex;
      margin: 0.83em 0;
      align-items: center;
    }
  }
}
</style>
