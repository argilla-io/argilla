<template>
  <div class="rule-metrics__container">
    <p class="rule-metrics__title">{{ title }}</p>
    <slot name="button-top" />
    <div class="rule-metrics">
      <template>
        <div
          :class="[metricsType, 'rule-metrics__item']"
          v-for="metric in metrics"
          :key="metric.name"
        >
          <p class="metric__title" :data-title="metricsTitle(metric)">
            {{ metric.name }}
          </p>
          <p class="metric__rule" v-if="!onlyOveralMetrics">
            <transition name="fade" mode="out-in" appear>
              <strong :key="metric.rule.value">{{ metric.rule.value }}</strong>
            </transition>
          </p>
          <span class="metric__overall">
            <template v-if="!onlyOveralMetrics">{{
              metric.overall.description
            }}</template>
            <transition name="fade" mode="out-in" appear>
              <span :key="metric.overall.value">
                {{ metric.overall.value }}
              </span>
            </transition>
          </span>
        </div>
      </template>
    </div>
    <slot name="button-bottom" />
  </div>
</template>

<script>
import { TextClassificationDataset } from "@/models/TextClassification";

export default {
  props: {
    dataset: {
      type: TextClassificationDataset,
      required: true,
    },

    title: {
      type: String,
      required: true,
    },

    metricsType: {
      type: String,
      default: "all",
      validator: (value) => {
        return ["all", "overall"].includes(value);
      },
    },
  },
  data: () => {
    return {
      metricsByRules: {},
      refresh: 0,
    };
  },
  computed: {
    rules() {
      return this.dataset.labelingRules;
    },
    metricsTotal() {
      return this.dataset.labelingRulesOveralMetrics || {};
    },

    currentRule() {
      return this.dataset.getCurrentLabelingRule();
    },

    ruleMetrics() {
      return this.dataset.getCurrentLabelingRuleMetrics() || {};
    },

    onlyOveralMetrics() {
      return this.metricsType === "overall";
    },

    placeholderFields() {
      return [
        "Precision",
        "Correct/incorrect",
        "Coverage",
        "Annotated coverage",
      ];
    },
    metrics() {
      return [
        {
          name: "Precision",
          overall: {
            description: "Avg:",
            tooltip: "Average fraction of correct labels given by the rules",
            value: this.formatNumber(this.metricsTotal.precisionAverage),
            refresh: this.refresh,
          },
          rule: {
            value: this.formatNumber(this.ruleMetrics.precision),
            tooltip: "Fraction of correct labels given by the rule",
          },
        },
        {
          name: "Correct/incorrect",
          overall: {
            description: "Total:",
            tooltip:
              "Total number of records the rules labeled correctly/incorrectly (if annotations are available)",
            value: isNaN(this.metricsTotal.totalCorrects)
              ? "_/_"
              : `${this.metricsTotal.totalCorrects}/${this.metricsTotal.totalIncorrects}`,
            refresh: this.refresh,
          },
          rule: {
            value: isNaN(this.ruleMetrics.correct)
              ? "_/_"
              : `${this.ruleMetrics.correct} / ${this.ruleMetrics.incorrect}`,
            tooltip:
              "Number of records the rule labeled correctly/incorrectly (if annotations are available)",
          },
        },
        {
          name: "Coverage",
          overall: {
            description: "Total:",
            tooltip: "Fraction of records labeled by any rule",
            value: this.formatNumber(this.metricsTotal.coverage),
          },
          rule: {
            value: this.formatNumber(this.ruleMetrics.coverage),
            tooltip: "Fraction of records labeled by the rule",
          },
        },
        {
          name: "Annotated coverage",
          overall: {
            description: "Total:",
            tooltip: "Fraction of annotated records labeled by any rule",
            value: this.formatNumber(this.metricsTotal.coverage_annotated),
          },
          rule: {
            value: this.formatNumber(this.ruleMetrics.coverage_annotated),
            tooltip: "Fraction of annotated records labeled by the rule",
          },
        },
      ];
    },
  },
  methods: {
    metricsTitle(metric) {
      return this.onlyOveralMetrics
        ? metric.overall.tooltip
        : metric.rule.tooltip;
    },

    formatNumber(value) {
      return isNaN(value) ? "-" : this.$options.filters.percent(value);
    },

    getValuesByMetricType(type) {
      return Object.keys(this.metricsByRules).map((key) => {
        return this.metricsByRules[key][type];
      });
    },
    getTotal(type) {
      return this.getValuesByMetricType(type).reduce(
        (accumulator, currentValue) => accumulator + currentValue,
        0
      );
    },
    getAverage(type) {
      return this.getTotal(type) / this.getValuesByMetricType(type).length;
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
    padding: 30px;
  }
  &__title {
    padding-bottom: 0;
    color: $lighter-color;
    @include font-size(22);
    font-weight: bold;
    margin-top: 0;
  }
  &__item {
    min-height: 82px;
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
            font-weight: 800;
          }
        }
      }
    }
    &.overall {
      span {
        display: block;
        @include font-size(20px);
        font-weight: 800;
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
