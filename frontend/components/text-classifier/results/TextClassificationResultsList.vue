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
  <results-list
    v-if="!viewSettings.visibleRulesList"
    :datasetId="datasetId"
    :datasetTask="datasetTask"
    @search-records="searchRecords"
  >
    <template slot="results-header">
      <rule-definition
        v-if="showRulesArea"
        :datasetId="datasetId"
        :datasetTask="datasetTask"
      />
    </template>
  </results-list>
  <rules-management
    class="content"
    v-else
    :datasetId="datasetId"
    :datasetTask="datasetTask"
    :datasetName="datasetName"
  />
</template>

<script>
import { getViewSettingsByDatasetName } from "@/models/viewSettings.queries";

export default {
  name: "TextClassificationResultsList",
  props: {
    datasetId: {
      type: Array,
      required: true,
    },
    datasetName: {
      type: String,
      required: true,
    },
    datasetTask: {
      type: String,
      required: true,
    },
  },
  computed: {
    viewSettings() {
      return getViewSettingsByDatasetName(this.datasetName);
    },
    showRulesArea() {
      return this.viewSettings.viewMode === "labelling-rules";
    },
  },
  methods: {
    searchRecords(query) {
      this.$emit("search-records", query);
    },
  },
};
</script>
<style lang="scss" scoped>
.content {
  @extend %collapsable-if-metrics !optional;
}
</style>
