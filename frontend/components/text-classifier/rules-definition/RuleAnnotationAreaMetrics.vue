<template>
  <div class="rules__metrics">
    <div v-for="metric in visibleMetrics" :key="metric.id">
      <p>{{ metric.name }}
        <span v-if="isNaN(metrics[metric.id])">-</span>
        <span v-else>{{ metrics[metric.id] | formatNumber }}</span>
      </p>
    </div>
  </div>
</template>

<script>
export default {
  data: () => {
    return {
      visibleMetrics: [
        { name: 'Coverage', id: 'coverage' },
        { name: 'Correct', id: 'correct' },
        { name: 'Incorrect', id: 'incorrect' },
        { name: 'Precision', id: 'precision' }
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
  margin-top: 3em;
  margin-bottom: 3em;
  max-width: 300px;
  display: flex;
  p {
    min-width: 25%;
    margin-right: 2em;
    span{
      display: block;
    }
  }
}
</style>


   