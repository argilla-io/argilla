<template>
  <div class="rules__metrics">
    <div v-for="metric in filteredMetrics" :key="metric.id">
      <p :data-title="metric.tooltip">{{ metric.name }}
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
          { name: 'Coverage', value: this.metrics.coverage, tooltip: 'Fraction of records labeled by the rule' },
          { name: 'Annotated Coverage', value: this.metrics.coverage_annotated, tooltip: 'Fraction of annotated records labeled by the rule' },
          { name: 'Correct', value: this.metrics.correct, tooltip: 'Number of records the rule labeled correctly (if annotations are available)' },
          { name: 'Incorrect', value: this.metrics.incorrect, tooltip: 'Number of records the rule labeled incorrectly (if annotations are available)' },
          { name: 'Precision', value: this.metrics.precision, tooltip: "Fraction of correct labels given by the rule" },
          { name: 'Records', value: Math.round(this.metrics.total_records * this.metrics.coverage), tooltip: 'Records matching the query' }
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
$color: #333346;
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
    strong {
      @include font-size(18px);
    }
  }
}
p[data-title] {
  position: relative;
  @extend %hastooltip;
  &:after {
    padding: 0.5em 1em;
    bottom: 100%;
    right: 50%;
    transform: translateX(50%);
    background: $color;
    color: white;
    border: none;
    border-radius: 3px;
    @include font-size(14px);
    font-weight: 600;
    margin-bottom: 0.5em;
    min-width: 180px;
    white-space: break-spaces;
  }
  &:before {
    right: 50%;
    top: -0.5em;
    border-top: 7px solid  $color;
    border-right: 7px solid transparent;
    border-left: 7px solid transparent;
  }
}
</style>


   