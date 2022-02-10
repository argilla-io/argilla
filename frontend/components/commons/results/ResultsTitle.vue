<template>
  <p class="records-title" v-if="dataset.results.total > 0">
    Records
    <span v-if="showWhenFiltered && areFiltersApplied.length"
      >with filters applied</span
    >
    ({{ dataset.results.total | formatNumber }})
  </p>
</template>

<script>
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
    showWhenFiltered: {
      type: Boolean,
      required: false,
    },
    excludedFilter: {
      type: Array,
      default: () => {
        return ["text"];
      },
    },
  },
  computed: {
    areFiltersApplied() {
      const appliedFilters = Object.keys(this.dataset.query)
        .filter((f) => !this.excludedFilter.includes(f))
        .map((key) => this.dataset.query[key]);
      return appliedFilters.filter((v) => v && Object.values(v).length);
    },
  },
};
</script>

<style lang="scss" scoped>

.records-title {
  color: $font-secondary;
}
</style>
