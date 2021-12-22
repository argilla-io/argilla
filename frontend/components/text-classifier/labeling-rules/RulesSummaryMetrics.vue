<template>
  <div class="rules-summary__metrics">
    <template v-if="!$fetchState.error && !$fetchState.pending">
      <p data-title="Average fraction of correct labels given by the rules">Precision average
        <span v-if="metricsTotal">{{getAverage('precision') | percent}}</span>
        <span v-else>-</span>
      </p>
      <p data-title="Total number of records the rules labeled correctly/incorrectly (if annotations are available)">Correct/incorrect
        <span v-if="metricsTotal">
          {{getTotal('correct')}}/{{getTotal('incorrect')}}
        </span>
        <span v-else>-</span>
      </p>
      <p data-title="Fraction of records labeled by any rule">Total coverage
        <span v-if="metricsTotal">
          {{metricsTotal.coverage | percent}}
        </span>
        <span v-else>-</span>
      </p>
      <p data-title="Fraction of annotated records labeled by any rule">Annotated coverage
        <span v-if="metricsTotal">
          {{metricsTotal.coverage_annotated | percent}}
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
$color: #333346;
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


