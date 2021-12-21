<template>
  <div class="rules-summary__metrics">
    <p>Precision average
      <span v-if="metricsTotal">{{getAverage('precision') | formatNumber}}</span>
      <span v-else>-</span>
    </p>
    <p>Total correct/incorrect
      <span v-if="metricsTotal">
        {{getTotal('correct')}}/{{getTotal('incorrect')}}
      </span>
      <span v-else>-</span>
    </p>
    <p>Total coverage
      <span v-if="metricsTotal">
        {{metricsTotal.coverage | formatNumber}}
      </span>
      <span v-else>-</span>
    </p>
    <p>Annotated coverage
      <span v-if="metricsTotal">
        {{metricsTotal.coverage_annotated | formatNumber}}
      </span>
      <span v-else>-</span>
    </p>
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
    },
    formattedRules: {
      type: Array,      
    },
  },
  data: () => {
    return {
      metricsTotal: undefined,
    }
  },
  async fetch() {
    if (this.formattedRules.length) {
      await this.getMetrics();
    }
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
    margin-bottom: 2em;
    @include font-size(15px);
    color: $font-secondary-dark;
    p {
      display: inline-block;
      margin-right: 2.5em;
      span {
        @include font-size(18px);
        display: block;
        color: palette(grey, dark);
        font-weight: 600;
      }
    }
  }
}
</style>


