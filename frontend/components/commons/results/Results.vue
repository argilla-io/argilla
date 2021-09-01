<template>
  <results-empty v-if="dataset.results.total === 0" />
  <div v-else class="results">
    <component :is="currentTaskResultsList" :dataset="dataset" />
  </div>
</template>

<script>
export default {
  props: {
    dataset: {
      type: Object,
      default: () => ({}),
    },
  },
  computed: {
    currentTaskResultsList() {
      return this.dataset.task + "ResultsList";
    },
  },
};
</script>

<style lang="scss" scoped>
.results {
  flex-grow: 2;
}
</style>
