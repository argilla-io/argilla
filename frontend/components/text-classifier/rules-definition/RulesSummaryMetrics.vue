<template>
  <div class="rules-summary__metrics">
    <p>Precision average<span>{{getAverage('precision') | formatNumber}}</span></p>
    <p>Total correct/incorrect<span class="correct">{{getTotal('correct')}}</span>/<span class="incorrect">{{getTotal('incorrect')}}</span>
    <p>Total coverage<span>{{metricsTotal.coverage | formatNumber}}</span></p>
    <p>Annotated coverage<span>{{metricsTotal.coverage_annotated | formatNumber}}</span></p>
  </div>
</template>

<script>
import { mapActions } from "vuex";
export default {
  props: {
    metricsByLabel: {
      type: Object,
    },
    dataset: {
      type: Object,      
    }
  },
  data: () => {
    return {
      metricsTotal: {}
    }
  },
  async fetch() {
    await this.getMetrics();
  },
  methods: {
    ...mapActions({
      getRulesMetrics: "entities/text_classification/getRulesMetrics",
    }),
    async getMetrics() {
      const response = await this.getRulesMetrics({
        dataset: this.dataset,
      })
      this.metricsTotal = response;
    },
    getTotal(type) {
      const reducer = (previousValue, currentValue) => previousValue + currentValue;
      const allValues = Object.keys(this.metricsByLabel).map(key => {
        return this.metricsByLabel[key][type];
      });
      return allValues.reduce(reducer);
    },
    getAverage(type) {
      const reducer = (previousValue, currentValue) => previousValue + currentValue;
      const allValues = Object.keys(this.metricsByLabel).map(key => {
        return this.metricsByLabel[key][type];
      });
      return allValues.reduce(reducer) / allValues.length;
    }
  }
}
</script>
<style lang="scss" scoped>
.rules-summary {
  &__metrics {
    display: inline-block;
    border-bottom: 1px solid $font-secondary-dark;
    margin-bottom: 2em;
    @include font-size(15px);
    color: $font-secondary-dark;
    p {
      display: inline-block;
      margin-right: 2.5em;
      span {
        margin-left: 1em;
      }
    }
    .correct {
      color: palette(green);
    }
    .incorrect {
      margin-left: 0;
      color: palette(red);
    }
  }
}
</style>


