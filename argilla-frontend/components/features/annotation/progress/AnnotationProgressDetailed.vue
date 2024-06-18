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
  <div v-if="datasetMetrics.hasMetrics" class="metrics">
    <BaseCircleProgress class="metrics__donut" :slices="progressItems" />
    <ul class="metrics__list">
      <li
        v-for="(status, index) in progressItems"
        :key="index"
        class="metrics__list__item"
      >
        <span
          class="color-bullet"
          :style="{ backgroundColor: status.color }"
        ></span>
        <label class="metrics__list__name" v-text="status.name" />
        <span
          class="metrics__list__counter"
          v-text="`(${getFormattedProgress(status.value)})`"
        />
      </li>
    </ul>
  </div>
</template>

<script>
import { RecordStatus } from "~/v1/domain/entities/record/RecordStatus";
import { useFeedbackTaskProgressViewModel } from "./useFeedbackTaskProgressViewModel";

export default {
  props: {
    datasetId: {
      type: String,
      required: true,
    },
    enableFetch: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    progressItems() {
      return [
        {
          name: RecordStatus.submitted.name,
          color: RecordStatus.submitted.color,
          value: this.datasetMetrics.submitted,
          percent: this.datasetMetrics.percentage.submitted,
        },
        {
          name: RecordStatus.draft.name,
          color: RecordStatus.draft.color,
          value: this.datasetMetrics.draft,
          percent: this.datasetMetrics.percentage.draft,
        },
        {
          name: RecordStatus.discarded.name,
          color: RecordStatus.discarded.color,
          value: this.datasetMetrics.discarded,
          percent: this.datasetMetrics.percentage.discarded,
        },
        {
          name: RecordStatus.pending.name,
          color: RecordStatus.pending.color,
          value: this.datasetMetrics.pending,
          percent: this.datasetMetrics.percentage.pending,
        },
      ];
    },
  },
  methods: {
    getFormattedProgress(progress) {
      return progress && this.$options.filters.formatNumber(progress);
    },
  },
  setup(props) {
    return useFeedbackTaskProgressViewModel(props);
  },
};
</script>

<style lang="scss" scoped>
$bullet-size: 10px;
.metrics {
  display: flex;
  align-items: center;
  gap: $base-space * 4;
  color: $black-54;
  padding: $base-space * 3 0;
  &__donut {
    flex-shrink: 0;
  }
}
.color-bullet {
  height: $bullet-size;
  width: $bullet-size;
  border-radius: $border-radius-rounded;
}

.metrics__list {
  display: grid;
  grid-template-columns: auto auto;
  column-gap: $base-space * 2;
  row-gap: $base-space;
  list-style: none;
  padding-left: 0;
  &__item {
    display: flex;
    align-items: center;
    gap: $base-space;
    @include font-size(13px);
    min-width: 140px;
  }
  &__name {
    text-transform: capitalize;
  }
}
</style>
