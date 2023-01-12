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
    v-if="!dataset.viewSettings.visibleRulesList"
    :dataset="dataset"
    @search-records="searchRecords"
  >
    <template slot="results-header">
      <rule-definition :dataset="dataset" v-if="showRulesArea" />
    </template>
  </results-list>
  <rules-management class="content" v-else :dataset="dataset" />
</template>

<script>
import { getViewSettingsWithPaginationByDatasetName } from "@/models/viewSettings.queries";

export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  computed: {
    viewSettings() {
      console.log(this.dataset.name);
      return getViewSettingsWithPaginationByDatasetName(this.dataset.name);
    },
    showRulesArea() {
      return this.dataset.viewSettings.viewMode === "labelling-rules";
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
