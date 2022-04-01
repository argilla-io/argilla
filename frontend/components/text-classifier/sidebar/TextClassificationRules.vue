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
      <p class="progress__info__text">Coverage</p>
      <span class="progress__info__percent">{{
        coverage.percent | percent
      }}</span>
    </div>
    <ReProgress
      re-mode="determinate"
      :progress="coverage.percent * 100"
    ></ReProgress>
    <div class="progress__info">
      <p class="progress__info__text">Annotated Coverage</p>
      <span class="progress__info__percent">{{
        annotatedCoverage.percent | percent
      }}</span>
    </div>
    <ReProgress
      re-mode="determinate"
      :progress="annotatedCoverage.percent * 100"
    ></ReProgress>
    <div class="progress__info">
      <p class="progress__info__text">Precision average</p>
      <span class="progress__info__percent">{{ precision | percent }}</span>
    </div>
    <div class="progress__info">
      <p class="progress__info__text">Correct/Incorrect</p>
      <span class="progress__info__percent">{{ correctAndIncorrect }}</span>
    </div>
    <div class="progress__info">
      <p class="progress__info__text">Total rules</p>
      <span class="progress__info__percent">{{ dataset.rules.length }}</span>
    </div>
    <template v-if="labels.length">
      <div class="scroll">
        <div v-for="label in labels" :key="label.index">
          <div class="info">
            <label>{{ label.label }}</label>
            <span class="records-number">{{
              label.counter | formatNumber
            }}</span>
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
    ruleMetrics() {
      return this.dataset.getCurrentLabelingRuleMetrics() || {};
    },
    metricsTotal() {
      return this.dataset.labelingRulesOveralMetrics || {};
    },
    labels() {
      const labelsInRules =
        this.dataset.rules.flatMap((rule) => rule.labels) || [];
      const availableLabels = this.dataset._labels.map((label) => {
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
  },
  methods: {
    formatNumber(value) {
      return isNaN(value) ? "-" : this.$options.filters.percent(value);
    },
  },
};
</script>
<style lang="scss" scoped>
.sidebar {
  &__title {
    color: $font-secondary-dark;
    margin-top: 0.5em;
    @include font-size(20px);
    font-weight: 700;
  }
}
label {
  display: block;
  width: calc(100% - 40px);
  overflow: hidden;
  text-overflow: ellipsis;
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
  color: $font-secondary-dark;
}
.scroll {
  max-height: calc(100vh - 450px);
  padding-right: 1em;
  margin-right: -1em;
  overflow: auto;
  .--paginated & {
    max-height: calc(100vh - 500px);
  }
}
.records-number {
  margin-right: 0;
  margin-left: auto;
}
.progress {
  float: right;
  line-height: 0.8em;
  font-weight: bold;
  &__info {
    display: flex;
    @include font-size(15px);
    align-items: center;
    color: $font-secondary-dark;
    font-weight: 600;
    margin-bottom: 1.5em;
    &__text {
      margin: 0;
    }
    &__percent {
      margin-top: 0;
      margin-right: 0;
      margin-left: auto;
    }
  }
  &__numbers {
    color: $font-secondary-dark;
    margin-bottom: 1.5em;
    @include font-size(18px);
    span {
      @include font-size(40px);
      font-weight: 700;
    }
  }
}
</style>
