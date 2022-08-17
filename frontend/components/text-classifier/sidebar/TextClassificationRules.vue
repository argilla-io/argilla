<!--
  - coding=utf-8
  - Copyright 2021-present, the Recognai S.L. team.
  -
  - Licensed under the Apache License, Version 2.0 (the "License");
  - you may not use this file except in compliance with the License.
  - You may obtain a copy of the License at
  -
  -     http://www.apache.org/licenses/LICENSE-2.0
  -
  - Unless required by applicable law or agreed to in writing, software
  - distributed under the License is distributed on an "AS IS" BASIS,
  - WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  - See the License for the specific language governing permissions and
  - limitations under the License.
  -->

<template>
  <div>
    <p class="sidebar__title">Overall rule metrics</p>
    <div class="progress__info">
      <p class="progress__info__text" :data-title="tooltip.coverage">
        Coverage
      </p>
      <span class="progress__info__percent">{{
        coverage.percent || 0 | percent
      }}</span>
    </div>
    <base-progress
      re-mode="determinate"
      color="#4C4EA3"
      :progress="coverage.percent * 100"
      :tooltip="`${coverage.records}/${totalRecords}`"
    ></base-progress>
    <div class="progress__info">
      <p class="progress__info__text" :data-title="tooltip.annotatedCoverage">
        Annotated Coverage
      </p>
      <span class="progress__info__percent">{{
        annotatedCoverage.percent || 0 | percent
      }}</span>
    </div>
    <base-progress
      re-mode="determinate"
      color="#A1A2CC"
      :progress="annotatedCoverage.percent * 100"
      :tooltip="`${annotatedCoverage.records}/${metricsTotal.annotated_records}`"
    ></base-progress>
    <div class="progress__info">
      <p class="progress__info__text" :data-title="tooltip.precision">
        Precision average
      </p>
      <transition name="fade" mode="out-in" appear
        ><span :key="precision" class="progress__info__percent">{{
          precision || 0 | percent
        }}</span></transition
      >
    </div>
    <div class="progress__info">
      <p class="progress__info__text" :data-title="tooltip.correctAndIncorrect">
        Correct/Incorrect
      </p>
      <transition name="fade" mode="out-in" appear
        ><span :key="correctAndIncorrect" class="progress__info__percent">{{
          correctAndIncorrect
        }}</span></transition
      >
    </div>
    <span class="space"></span>
    <div class="progress__info">
      <p class="progress__info__text">Total rules</p>
      <transition name="fade" mode="out-in" appear
        ><span :key="dataset.rules.length" class="progress__info__percent">{{
          dataset.rules.length
        }}</span></transition
      >
    </div>
    <template v-if="labels.length">
      <div class="scroll">
        <div v-for="label in labels" :key="label.index">
          <div class="info">
            <label>{{ label.label }}</label>
            <transition name="fade" mode="out-in" appear
              ><span class="records-number">{{
                label.counter | formatNumber
              }}</span></transition
            >
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
export default {
  // TODO clean and typify
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data: () => {
    return {};
  },
  computed: {
    tooltip() {
      return {
        coverage: "Percentage of records labeled by all rules",
        annotatedCoverage:
          "Percentage of annotated records labeled by all rules",
        precision: "Percentage of correct labels given by all rules",
        correctAndIncorrect:
          "Number of labels the rule predicted correctly/incorrectly with respect to the annotations",
      };
    },
    ruleMetrics() {
      return this.dataset.getCurrentLabelingRuleMetrics() || {};
    },
    metricsTotal() {
      return this.dataset.labelingRulesOveralMetrics || {};
    },
    labels() {
      const labelsInRules =
        this.dataset.rules.flatMap((rule) => rule.labels) || [];
      const availableLabels = this.dataset.labels.map((label) => {
        return {
          label: label,
          counter: labelsInRules.filter((l) => l === label).length || 0,
        };
      });
      return (
        availableLabels.sort((a, b) => (a.counter > b.counter ? -1 : 1)) || []
      );
    },
    coverage() {
      return {
        percent: this.metricsTotal.coverage,
        records: this.$options.filters.formatNumber(
          Math.round(
            this.metricsTotal.coverage * this.dataset.globalResults.total
          ) || 0
        ),
      };
    },
    annotatedCoverage() {
      return {
        percent: this.metricsTotal.coverage_annotated,
        records: this.$options.filters.formatNumber(
          Math.round(
            this.metricsTotal.coverage_annotated *
              this.metricsTotal.annotated_records
          ) || 0
        ),
      };
    },
    precision() {
      return this.metricsTotal.precisionAverage;
    },
    correctAndIncorrect() {
      return isNaN(this.metricsTotal.totalCorrects)
        ? "-/-"
        : `${this.metricsTotal.totalCorrects}/${this.metricsTotal.totalIncorrects}`;
    },
    totalRecords() {
      return this.$options.filters.formatNumber(
        this.dataset.globalResults.total
      );
    },
  },
  methods: {
    formatNumber(value) {
      return isNaN(value) ? "-" : this.$options.filters.percent(value);
    },
  },
};
</script>
<style lang="scss" scoped>
$color: #333346;
label {
  display: block;
  width: calc(100% - 40px);
  hyphens: auto;
  word-break: break-word;
}
.labels {
  margin-top: 3em;
  strong {
    margin-bottom: 1em;
    display: block;
  }
}
.info {
  position: relative;
  display: flex;
  margin-bottom: 0.7em;
  color: $font-secondary-medium-dark;
}
.scroll {
  max-height: calc(100vh - 400px);
  padding-right: 1em;
  margin-right: -1em;
  overflow: auto;
  @extend %hide-scrollbar;
}
.records-number {
  margin-right: 0;
  margin-left: auto;
}
.space {
  margin-bottom: 2em;
  display: block;
}
.progress {
  float: right;
  line-height: 0.8em;
  font-weight: bold;
  &__info {
    display: flex;
    @include font-size(15px);
    align-items: center;
    color: $font-secondary-medium-dark;
    font-weight: 600;
    margin-bottom: 0.5em;
    margin-top: 1em;
    &__text {
      margin: 0;
    }
    &__percent {
      margin-top: 0;
      margin-right: 0;
      margin-left: auto;
    }
  }
}
p[data-title] {
  position: relative;
  @extend %has-tooltip--top;
  @extend %tooltip-large-text;
}
</style>
