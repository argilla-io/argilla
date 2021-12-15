<template>
  <div class="rules__metrics">
    <div class="rules__metrics__header">
      <span>Coverage</span>
      <span>Correct</span>
      <span>Incorrect</span>
      <span>Precision</span>
    </div>
    <div class="rules__metrics__header">
      <span>{{metrics.coverage ? metrics.coverage : '-'}}</span>
      <span>{{metrics.correct ? metrics.correct : '-'}}</span>
      <span>{{metrics.incorrect ? metrics.incorrect : '-'}}</span>
      <span>{{metrics.precision ? metrics.precision : '-'}}</span>
    </div>
  </div>
</template>

<script>
export default {
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
  span {
    min-width: 25%;
  }
  &__header {
    display: flex;
  }
  &__body {
    display: flex;
  }
}
</style>


   