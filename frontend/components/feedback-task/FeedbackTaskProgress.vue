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
  <SidebarFeedbackTaskProgress
    v-if="datasetMetrics"
    :progressTotal="datasetMetrics.total_record"
    :totalSubmitted="datasetMetrics.responses_submitted"
    :totalDiscarded="datasetMetrics.responses_discarded"
  />
</template>

<script>
import { getDatasetMetricsByDatasetIdAndUser } from "@/models/feedback-task-model/dataset-metric/datasetMetric.queries";

export default {
  props: {
    userIdToShowMetrics: {
      type: String,
      required: true,
    },
  },
  computed: {
    datasetId() {
      return this.$route.params.id;
    },
    datasetMetrics() {
      return getDatasetMetricsByDatasetIdAndUser({
        datasetId: this.datasetId,
        userId: this.userIdToShowMetrics,
      });
    },
  },
};
</script>
