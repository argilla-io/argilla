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
  },
  computed: {
    progressRanges() {
      return [
        {
          id: "discarded",
          name: "progress",
          color: "linear-gradient(90deg, #6A6A6C 0%, #252626 100%)",
          value: this.progressNotPending,
        },
        {
          id: "pending",
          name: "progress",
          color: "linear-gradient(90deg, #EFEFEF 0%, #D3D3D3 100%)",
          value: this.datasetMetrics.pending,
        },
      ];
    },
    progressNotPending() {
      return this.datasetMetrics.total - this.datasetMetrics.pending;
    },
    progressItems() {
      return [
        {
          name: RecordStatus.submitted.name,
          color: this.submittedColor,
          value: this.datasetMetrics.submitted,
          percent: this.getPercent(this.datasetMetrics.submitted),
        },
        {
          name: RecordStatus.draft.name,
          color: this.draftColor,
          value: this.datasetMetrics.draft,
          percent: this.getPercent(this.datasetMetrics.draft),
        },
        {
          name: RecordStatus.discarded.name,
          color: this.discardedColor,
          value: this.datasetMetrics.discarded,
          percent: this.getPercent(this.datasetMetrics.discarded),
        },
        {
          name: RecordStatus.pending.name,
          color: this.pendingColor,
          value: this.datasetMetrics.pending,
          percent: this.getPercent(this.datasetMetrics.pending),
        },
      ];
    },
    pendingColor() {
      return RecordStatus.pending.color;
    },
    draftColor() {
      return RecordStatus.draft.color;
    },
    submittedColor() {
      return RecordStatus.submitted.color;
    },
    discardedColor() {
      return RecordStatus.discarded.color;
    },
  },
  methods: {
    getFormattedProgress(progress) {
      return progress && this.$options.filters.formatNumber(progress);
    },
    getPercent(progress) {
      return (progress / this.datasetMetrics.total) * 100;
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
    flex: 1;
    min-width: 40%;
    @include font-size(13px);
  }
  &__name {
    text-transform: capitalize;
  }
}
</style>
