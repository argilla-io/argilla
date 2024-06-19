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
    :progress-completed="datasetMetrics.submitted + datasetMetrics.discarded"
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
    enableFetch: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    progressRanges() {
      return [
        {
          id: "completed",
          name: "completed",
          color: "linear-gradient(90deg, #6A6A6C 0%, #252626 100%)",
          value: this.datasetMetrics.submitted + this.datasetMetrics.discarded,
        },
        {
          id: "pending",
          name: "progress",
          color: "linear-gradient(white)",
          value: this.datasetMetrics.pending + this.datasetMetrics.draft,
        },
      ];
    },
  },
  setup(props) {
    return useFeedbackTaskProgressViewModel(props);
  },
};
</script>
