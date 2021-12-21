<template>
  <div class="rules__metrics">
    <div v-for="metric in filteredMetrics" :key="metric.id">
      <p>{{ metric.name }}
        <span v-if="isNaN(metric.value)">-</span>
        <strong v-else>{{ metric.value | formatNumber }}</strong>
      </p>
    </div>
  </div>
</template>

<script>
export default {
  computed: {
      filteredMetrics() {
        return [ 
          { name: 'Coverage', value: this.metrics.coverage },
          { name: 'Annotated Coverage', value: this.metrics.coverage_annotated },
          { name: 'Correct', value: this.metrics.correct },
          { name: 'Incorrect', value: this.metrics.incorrect },
          { name: 'Precision', value: this.metrics.precision },
          { name: 'Records matching the query', value: Math.round(this.metrics.total_records * this.metrics.coverage) }
        ]
      }
  },
  props: {
    metrics: {
      type: Object,
    }
  }
}
</script>
<style lang="scss" scoped>
.rules__metrics {
  margin-top: 1em;
  margin-bottom: 3em;
  max-width: 300px;
  display: flex;
  p {
    min-width: 25%;
    white-space: nowrap;
    margin-right: 2em;
    span, strong {
      display: block;
    }
  }
}
</style>


   