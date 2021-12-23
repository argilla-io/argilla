<template>
  <div class="rules-global__metrics">
    <template v-if="!$fetchState.error && !$fetchState.pending">
      <p :data-title="metric.tooltip" v-for="metric in metrics" :key="metric.name">
        {{metric.name}}
        <span v-if="!isNaN(metric.operation) && metric.value !== '0/0'">
          <template v-if="metric.type === 'percent'">
            {{metric.value | percent}}
          </template>
          <template v-else>
            {{metric.value}}
          </template>
        </span>
        <span v-else>-</span>
      </p>
    </template>
  </div>
</template>

<script>
import { mapActions } from "vuex";
export default {
  props: {
    rules: {
      type: Array,
    },
    dataset: {
      type: Object,      
    },
  },
  data: () => {
    return {
      metricsByLabel: {},
      metricsTotal: undefined,
    }
  },
  computed: {
    metrics() {
      return [
        { name: 'Precision average', tooltip: 'Average fraction of correct labels given by the rules', value: this.getAverage('precision'), type: 'percent', operation: (this.getAverage('precision'))},
        { name: 'Correct/incorrect', tooltip: 'Total number of records the rules labeled correctly/incorrectly (if annotations are available)', value: `${this.getTotal('correct')}/${this.getTotal('incorrect')}`, operation: this.getTotal('correct') },
        { name: 'Total coverage', tooltip: 'Fraction of records labeled by any rule', value: this.metricsTotal ? this.metricsTotal.coverage : '-', type: 'percent', operation: this.metricsTotal ? this.metricsTotal.coverage : NaN },
        { name: 'Annotated coverage', tooltip: 'Fraction of annotated records labeled by any rule', value: this.metricsTotal ? this.metricsTotal.coverage_annotated : '-', type: 'percent', operation: this.metricsTotal ? this.metricsTotal.coverage_annotated : NaN  },
      ]
    }
  },
  async fetch() {
    if (this.rules.length) {
      await this.getMetrics();
      await this.getMetricsByLabel();
    }
  },
  methods: {
    ...mapActions({
      getRulesMetrics: "entities/text_classification/getRulesMetrics",
      getRuleMetricsByLabel: "entities/text_classification/getRuleMetricsByLabel",
    }),
    async getMetrics() {
      const response = await this.getRulesMetrics({
        dataset: this.dataset,
      })
      this.metricsTotal = response;
    },
    async getMetricsByLabel() {
      const responses = await Promise.all(
        this.rules.map((rule) => {
          return this.getRuleMetricsByLabel({
            dataset: this.dataset,
            query: rule.query,
            label: rule.label,
          });
        })
      );

      responses.forEach((response, idx) => {
        this.metricsByLabel[this.rules[idx].query] = response;
      });
    },
    getTotal(type) {
      const reducer = (previousValue, currentValue) => previousValue + currentValue;
      const allValues = Object.keys(this.metricsByLabel).map(key => {
        return this.metricsByLabel[key][type];
      });
      return allValues.reduce(reducer, 0);
    },
    getAverage(type) {
      const reducer = (previousValue, currentValue) => previousValue + currentValue;
      const allValues = Object.keys(this.metricsByLabel).map(key => {
        return this.metricsByLabel[key][type];
      });
      return allValues.reduce(reducer, 0) / allValues.length;
    }
  }
}
</script>
<style lang="scss" scoped>
$color: #333346;
.rules-global {
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
    min-width: 200px;
    white-space: break-spaces;
  }
  &:before {
    right: calc(50% - 7px);
    top: -0.5em;
    border-top: 7px solid  $color;
    border-right: 7px solid transparent;
    border-left: 7px solid transparent;
  }
}
</style>


