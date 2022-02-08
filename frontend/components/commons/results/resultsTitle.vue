<template>
  <p class="records-title" v-if="dataset.results.total > 0">
    Records
    <template v-if="filtersApplied.length">with filters applied</template> ({{
      dataset.results.total | formatNumber
    }})
  </p>
</template>

<script>
export default {
  props: {
    dataset: {
      dataset: {
        type: Object,
        required: true
      }
    }
  },
  computed: {
    filtersApplied() {
      return Object.values(this.dataset.query).filter(
        v => v && Object.values(v).length
      );
    }
  }
};
</script>

<style lang="scss" scoped>
.records-title {
  color: $font-secondary;
}
</style>


