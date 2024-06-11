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
  <BarProgress
    v-if="datasetMetrics.hasMetrics"
    :loading="false"
    :progress-ranges="progressRanges"
    :progress-not-pending="progressNotPending"
    :total="datasetMetrics.total"
  />
</template>

<script>
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
          id: "not-pending",
          name: "not-pending",
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
  },
  setup(props) {
    return useFeedbackTaskProgressViewModel(props);
  },
};
</script>

<style lang="scss" scoped>
.metrics {
  color: $black-54;
}
.color-bullet {
  height: $base-space;
  width: $base-space;
  border-radius: $border-radius-rounded;
  display: inline-block;
}
:deep() {
  .metrics__list {
    list-style: none;
    padding-left: 0;
    margin-bottom: $base-space * 3;
    &__item {
      display: flex;
      align-items: center;
      gap: $base-space;
      margin-bottom: $base-space;
      @include font-size(13px);
    }
    &__name {
      text-transform: capitalize;
      display: block;
      width: calc(100% - 40px);
      hyphens: auto;
      word-break: break-word;
    }
    &__counter {
      margin-right: 0;
      margin-left: auto;
    }
  }
}
</style>
