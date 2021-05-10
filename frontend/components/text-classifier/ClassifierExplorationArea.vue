<template>
  <div>
    <LabelPill class="predictions" :labels="showLabels" :showConfidence="true"/>
  </div>
</template>
<script>
import "assets/icons/ignore";

export default {
  props: {
    labels: {
      type: Array,
      required: true,
    }
  },
  data: () => ({
    maxLabels: 16,
  }),
  computed: {
    showLabels() {
      if (this.labels.length > this.maxLabels) {
        return this.labels.slice(0, this.maxLabels)
      }
      return this.labels
    }
  }
}
</script>
<style lang="scss" scoped>
// @import "@recognai/re-commons/src/assets/scss/components/tooltip.scss";

</style>
