<template>
  <div class="rule-metrics__container">
    <p class="rule-metrics__title">{{ title }}</p>
    <slot name="button-top" />
    <template v-if="!$fetchState.error && !$fetchState.pending">
      <div class="rule-metrics">
        <div
          :class="[metricsType, 'rule-metrics__item']"
          v-for="metric in metrics"
          :key="metric.name"
        >
          <p
            class="metric__title"
            :data-title="
              metricsType === 'overall'
                ? metric.overall.tooltip
                : metric.rule.tooltip
            "
          >
            {{ metric.name }}
          </p>
          <template v-if="metricsType !== 'overall'">
            <p class="metric__rule">
              <transition name="fade" mode="out-in" appear>
                <strong
                  :key="metric.rule.value"
                  v-if="metric.rule.type === 'percent'"
                  >{{ metric.rule.value | percent }}</strong
                >
                <strong :key="metric.rule.value" v-else>{{
                  metric.rule.value
                }}</strong>
              </transition>
            </p>
          </template>
          <template v-if="metricsType !== 'rule'">
            <span class="metric__overall">
              <template v-if="metricsType === 'all'">{{
                metric.overall.description
              }}</template>
              <transition name="fade" mode="out-in" appear>
                <span v-if="metric.overall.type === 'percent'">
                  {{ metric.overall.value | percent }}
                </span>
                <span v-else>
                  {{ metric.overall.value }}
                </span>
              </transition>
            </span>
          </template>
        </div>
      </div>
    </template>
    <slot name="button-bottom" />
  </div>
</template>

<script>
import { mapActions } from "vuex";
export default {
  props: {
    title: {
      type: String,
      default: "Metrics",
    },
    dataset: {
      type: Object,
      required: true,
    },
    metricsType: {
      type: String,
      default: "all",
      validator: (value) => {
        return ["all", "overall", "rule"].includes(value);
      },
    },
    activeLabel: {
      type: String,
    },
  },
  data: () => {
    return {
      rules: undefined,
      metricsByLabel: {},
      metricsByRules: {},
      metricsTotal: undefined,
    };
  },
  async fetch() {
    await this.getAllRules();
    await this.getMetricsByLabel();
    if (this.rules.length) {
      await Promise.all([this.getMetrics(), this.getMetricsByRules()]);
    }
  },
  computed: {
    metrics() {
      return [
        {
          name: "Precision",
          overall: {
            description: "Avg:",
            tooltip: "Average fraction of correct labels given by the rules",
            value: this.getAverage("precision") || 0,
            type: "percent",
            operation: this.getAverage("precision"),
          },
          rule: {
            type: "percent",
            value: this.metricsByLabel.precision || 0,
            tooltip: "Fraction of correct labels given by the rule",
          },
        },
        {
          name: "Correct/incorrect",
          overall: {
            description: "Total:",
            tooltip:
              "Total number of records the rules labeled correctly/incorrectly (if annotations are available)",
            value: this.getTotal("correct")
              ? `${this.getTotal("correct")}/${this.getTotal("incorrect")}`
              : "_/_",
            operation: this.getTotal("correct"),
          },
          rule: {
            value:
              this.metricsByLabel.correct !== undefined
                ? `${this.metricsByLabel.correct}/${this.metricsByLabel.incorrect}`
                : "_/_",
            tooltip:
              "Number of records the rule labeled correctly/incorrectly (if annotations are available)",
          },
        },
        {
          name: "Coverage",
          overall: {
            description: "Total:",
            tooltip: "Fraction of records labeled by any rule",
            value: this.metricsTotal ? this.metricsTotal.coverage : 0,
            type: "percent",
            operation: this.metricsTotal ? this.metricsTotal.coverage : NaN,
          },
          rule: {
            type: "percent",
            value: this.metricsByLabel.coverage || 0,
            tooltip: "Fraction of records labeled by the rule",
          },
        },
        {
          name: "Annotated coverage",
          overall: {
            description: "Total:",
            tooltip: "Fraction of annotated records labeled by any rule",
            value: this.metricsTotal ? this.metricsTotal.coverage_annotated : 0,
            type: "percent",
            operation: this.metricsTotal
              ? this.metricsTotal.coverage_annotated
              : NaN,
          },
          rule: {
            type: "percent",
            value: this.metricsByLabel.coverage_annotated || 0,
            tooltip: "Fraction of annotated records labeled by the rule",
          },
        },
      ];
    },
    recordsMetric() {
      return {
        name: "Records",
        value:
          Math.round(
            this.metricsByLabel.total_records * this.metricsByLabel.coverage
          ) || 0,
        tooltip: "Records matching the query",
      };
    },
  },
  watch: {
    async activeLabel(n, o) {
      if (n !== o) {
        await this.getMetricsByLabel();
      }
    },
    recordsMetric(n) {
      this.$emit("records-metric", n);
    },
  },
  methods: {
    ...mapActions({
      getRules: "entities/text_classification/getRules",
      getRulesMetrics: "entities/text_classification/getRulesMetrics",
      getRuleMetricsByLabel:
        "entities/text_classification/getRuleMetricsByLabel",
    }),
    async getAllRules() {
      this.rules = await this.getRules({ dataset: this.dataset });
    },
    async getMetrics() {
      this.metricsTotal = await this.getRulesMetrics({
        dataset: this.dataset,
      });
    },
    async getMetricsByRules() {
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
        this.metricsByRules[this.rules[idx].query] = response;
      });
    },
    async getMetricsByLabel() {
      if (this.activeLabel !== undefined) {
        const response = await this.getRuleMetricsByLabel({
          dataset: this.dataset,
          query: this.dataset.query.text,
          label: this.activeLabel,
        });
        this.metricsByLabel = response;
      } else {
        this.metricsByLabel = {};
      }
    },
    getTotal(type) {
      const reducer = (previousValue, currentValue) =>
        previousValue + currentValue;
      const allValues = Object.keys(this.metricsByRules).map((key) => {
        return this.metricsByRules[key][type];
      });
      return allValues.reduce(reducer, 0);
    },
    getAverage(type) {
      const reducer = (previousValue, currentValue) =>
        previousValue + currentValue;
      const allValues = Object.keys(this.metricsByRules).map((key) => {
        return this.metricsByRules[key][type];
      });
      return allValues.reduce(reducer, 0) / allValues.length;
    },
  },
};
</script>
<style lang="scss" scoped>
$color: #333346;
.rule-metrics {
  &__container {
    position: relative;
    display: flex;
    flex-flow: column;
    max-height: 410px;
    background: $primary-color;
    margin-left: 1em;
    color: $lighter-color;
    border-radius: 5px;
    margin-bottom: 2em;
    padding: 20px;
  }
  &__title {
    padding-bottom: 0;
    color: $lighter-color;
    @include font-size(22);
    font-weight: bold;
    margin-top: 0;
  }
  &__item {
    &.all {
      .metric {
        &__rule {
          @include font-size(20px);
          font-weight: 600;
          margin-top: 0.2em;
          margin-bottom: 0.2em;
        }
        &__overall {
          span {
            font-weight: 600;
          }
        }
      }
    }
    &.overall {
      span {
        display: block;
        @include font-size(20px);
        font-weight: 600;
        margin-top: 0.2em;
      }
    }
  }
}
.metric {
  &__title {
    display: inline-block;
    @include font-size(14px);
    font-weight: 600;
    margin-bottom: 0;
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
    min-width: 220px;
    white-space: break-spaces;
  }
  &:before {
    right: calc(50% - 7px);
    top: -0.5em;
    border-top: 7px solid $color;
    border-right: 7px solid transparent;
    border-left: 7px solid transparent;
  }
}
</style>
