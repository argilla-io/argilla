<template>
  <div class="rule-metrics__container">
    <p class="rule-metrics__title">{{ title }}</p>
    <slot name="button-top" />
    <div class="rule-metrics">
      <template v-if="$fetchState.pending">
        <div
          class="rule-metrics__item"
          v-for="(field, index) in placeholderFields"
          :key="index"
        >
          <p class="metric__title">{{ field }}</p>
          <p class="metric__placeholder">-</p>
        </div>
      </template>
      <template v-else-if="!$fetchState.error">
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
          <p class="metric__rule" v-if="metricsType !== 'overall'">
            <transition name="fade" mode="out-in" appear>
              <strong :key="metric.rule.value">{{ metric.rule.value }}</strong>
            </transition>
          </p>
          <span class="metric__overall" v-if="metricsType !== 'rule'">
            <template v-if="metricsType === 'all'">{{
              metric.overall.description
            }}</template>
            <transition name="fade" mode="out-in" appear>
              <span v-html="metric.overall.value" :key="metric.overall.value" />
            </transition>
          </span>
        </div>
      </template>
    </div>
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
    rules: {
      type: Array,
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
      metricsByLabel: {},
      metricsByRules: {},
      metricsTotal: {},
      refresh: 0,
    };
  },
  async fetch() {
    await this.getMetricsByLabel();
    if (this.rules.length) {
      await this.getMetrics();
      await this.getMetricsByRules();
    }
  },
  computed: {
    query() {
      return this.dataset.query.text;
    },
    placeholderFields() {
      return [
        "Coverage",
        "Annotated coverage",
        "Precision",
        "Correct/incorrect",
      ];
    },
    metrics() {
      return [
        {
          name: "Coverage",
          overall: {
            description: "Total:",
            tooltip: "Percentage of records labeled by any rule",
            value: `${this.formatNumber(
              this.metricsTotal.coverage
            )} <span class="records-number">(${this.$options.filters.formatNumber(
              Math.round(
                this.metricsTotal.coverage * this.dataset.globalResults.total
              )
            )} records)</span>`,
          },
          rule: {
            value: this.formatNumber(this.metricsByLabel.coverage),
            tooltip: "Percentage of records labeled by the rule",
          },
        },
        {
          name: "Annotated coverage",
          overall: {
            description: "Total:",
            tooltip: "Percentage of annotated records labeled by any rule",
            value: `${this.formatNumber(
              this.metricsTotal.coverage_annotated
            )} <span class="records-number">(${this.$options.filters.formatNumber(
              Math.round(
                this.metricsTotal.coverage_annotated *
                  this.dataset.globalResults.total
              )
            )} records)</span>`,
          },
          rule: {
            value: this.formatNumber(this.metricsByLabel.coverage_annotated),
            tooltip: "Percentage of annotated records labeled by the rule",
          },
        },
        {
          name: "Precision",
          overall: {
            description: "Avg:",
            tooltip: "Average percentage of correct labels given by the rules",
            value: this.formatNumber(this.getAverage("precision")),
            refresh: this.refresh,
          },
          rule: {
            value: this.formatNumber(this.metricsByLabel.precision),
            tooltip: "Percentage of correct labels given by the rule",
          },
        },
        {
          name: "Correct/incorrect",
          overall: {
            description: "Total:",
            tooltip:
              "Total number of records the rules labeled correctly/incorrectly (if annotations are available)",
            value: Object.keys(this.metricsByRules).length
              ? `${this.getTotal("correct")}/${this.getTotal("incorrect")}`
              : "-/-",
            refresh: this.refresh,
          },
          rule: {
            value:
              this.metricsByLabel.correct !== undefined
                ? `${this.metricsByLabel.correct}/${this.metricsByLabel.incorrect}`
                : "-/-",
            tooltip:
              "Number of records the rule labeled correctly/incorrectly (if annotations are available)",
          },
        },
      ];
    },
    recordsMetric() {
      return {
        name: "Records",
        value: isNaN(this.metricsByLabel.total_records)
          ? "-"
          : this.$options.filters.formatNumber(
              Math.round(
                this.metricsByLabel.total_records * this.metricsByLabel.coverage
              )
            ),
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
    async rules(n, o) {
      if (n !== o) {
        if (this.rules.length) {
          await Promise.all([this.getMetrics(), this.getMetricsByRules()]);
        }
        this.refresh++;
      }
    },
    recordsMetric(n) {
      this.$emit("records-metric", n);
    },
  },
  methods: {
    ...mapActions({
      getRulesMetrics: "entities/text_classification/getRulesMetrics",
      getRuleMetricsByLabel:
        "entities/text_classification/getRuleMetricsByLabel",
    }),

    formatNumber(value) {
      return isNaN(value) ? "-" : this.$options.filters.percent(value);
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
      if (this.query !== undefined) {
        const response = await this.getRuleMetricsByLabel({
          dataset: this.dataset,
          query: this.query,
          label: this.activeLabel,
        });
        this.metricsByLabel = response;
      } else {
        this.metricsByLabel = {};
      }
    },
    getValuesByMetricType(type) {
      return Object.keys(this.metricsByRules).map((key) => {
        return this.metricsByRules[key][type] || 0;
      });
    },
    getTotal(type) {
      return this.getValuesByMetricType(type).reduce(
        (accumulator, currentValue) => accumulator + currentValue,
        0
      );
    },
    getAverage(type) {
      const filteredValues = Object.keys(this.metricsByRules)
        .filter((key) => this.metricsByRules[key].coverage_annotated > 0)
        .map((k) => {
          return this.metricsByRules[k][type];
        });
      return this.getTotal(type) / filteredValues.length;
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

<style lang="scss">
.records-number {
  @include font-size(16px);
  font-weight: normal;
  .all & {
    display: none;
  }
}
</style>
