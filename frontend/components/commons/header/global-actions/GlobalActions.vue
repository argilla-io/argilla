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
  <div v-if="showGlobalActions" class="container">
    <div class="global-actions">
      <validate-discard-action
        :datasetId="datasetId"
        :datasetTask="datasetTask"
        :visibleRecords="datasetVisibleRecords"
        :availableLabels="availableLabels"
        :isMultiLabel="isMultiLabel"
        @discard-records="onDiscard"
        @validate-records="onValidate"
        @clear-records="onClear"
        @reset-records="onReset"
        @on-select-labels="onSelectLabels($event)"
      />
      <create-new-action v-if="isCreationLabel" @new-label="onNewLabel" />
    </div>
  </div>
</template>

<script>
import { getViewSettingsWithPaginationByDatasetName } from "@/models/viewSettings.queries";
export default {
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
    datasetVisibleRecords: {
      type: Array,
      required: true,
    },
    isCreationLabel: {
      type: Boolean,
      default: () => false,
    },
    availableLabels: {
      type: Array,
      default: () => [],
    },
    isMultiLabel: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    viewSettings() {
      return getViewSettingsWithPaginationByDatasetName(this.datasetName);
    },
    annotationEnabled() {
      return this.viewSettings.viewMode === "annotate";
    },
    paginationSizeIsOne() {
      return this.viewSettings.pagination.size === 1;
    },
    showGlobalActions() {
      return this.annotationEnabled && !this.paginationSizeIsOne;
    },
  },
  methods: {
    onValidate($event) {
      this.$emit("validate-records", $event);
    },
    onDiscard($event) {
      this.$emit("discard-records", $event);
    },
    onClear($event) {
      this.$emit("clear-records", $event);
    },
    onReset($event) {
      this.$emit("reset-records", $event);
    },
    onSelectLabels($event) {
      this.$emit("on-select-labels", $event);
    },
    onNewLabel($event) {
      this.$emit("new-label", $event);
    },
  },
};
</script>

<style lang="scss" scoped>
.container {
  @extend %container;
  margin: 0 auto auto 0;
  padding-top: 0;
  padding-bottom: 0;
  padding-left: 4em;
  @extend %collapsable-if-metrics !optional;
}
.global-actions {
  display: flex;
  align-items: center;
  width: 100%;
  text-align: left;
  padding: 1em $base-space * 2;
  background: palette(white);
  border-radius: $border-radius-m;
  position: relative;
  box-shadow: $shadow-300;
  margin-bottom: $base-space * 2;
}
</style>
