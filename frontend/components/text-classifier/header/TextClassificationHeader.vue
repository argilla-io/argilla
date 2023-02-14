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
  <div class="header__filters">
    <filters-area
      v-if="!dataset.viewSettings.visibleRulesList"
      :dataset="dataset"
      :enableSimilaritySearch="enableSimilaritySearch"
      @search-records="searchRecords"
    >
      <dataset-options :dataset="dataset" />
    </filters-area>
    <global-actions
      :datasetId="datasetId"
      :datasetName="datasetName"
      :datasetTask="datasetTask"
      :datasetVisibleRecords="dataset.visibleRecords"
      :availableLabels="availableLabels"
      :isCreationLabel="allowLabelCreation"
      :isMultiLabel="isMultiLabel"
      @discard-records="onDiscard"
      @validate-records="onValidate"
      @clear-records="onClear"
      @reset-records="onReset"
      @on-select-labels="onSelectLabels($event)"
      @new-label="onNewLabel"
    />
  </div>
</template>

<script>
import { mapActions } from "vuex";
import { getDatasetFromORM } from "@/models/dataset.utilities";
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
    enableSimilaritySearch: {
      type: Boolean,
      required: true,
    },
  },
  computed: {
    dataset() {
      //TODO when refactor of filter part from header, remove this computed/and get only what is necessary as props
      return getDatasetFromORM(this.datasetId, this.datasetTask, true);
    },
    isMultiLabel() {
      return this.dataset.isMultiLabel;
    },
    availableLabels() {
      const record = this.dataset.results.records[0];
      let labels =
        record && record.prediction
          ? record.prediction.labels.map((label) => label.class)
          : [];
      labels = Array.from(new Set([...labels, ...this.dataset.labels]));
      return labels;
    },
    allowLabelCreation() {
      return !this.dataset.settings.label_schema;
    },
  },
  methods: {
    ...mapActions({
      updateRecords: "entities/datasets/updateDatasetRecords",
      discard: "entities/datasets/discardAnnotations",
      validate: "entities/datasets/validateAnnotations",
      resetRecords: "entities/datasets/resetRecords",
    }),
    async onSelectLabels({ labels, selectedRecords }) {
      const records = selectedRecords.map((record) => {
        const pendingStatusProperties = {
          selected: true,
          status: "Edited",
        };
        return {
          ...record,
          ...(this.isMultiLabel && pendingStatusProperties),
          currentAnnotation: {
            agent: this.$auth.user.username,
            labels: this.formatLabels(labels),
          },
        };
      });
      const updatedRecords = {
        dataset: this.dataset,
        agent: this.$auth.user.username,
        records: records,
      };
      if (this.isMultiLabel) {
        await this.updateRecords(updatedRecords);
      } else {
        await this.onValidate(records);
      }
    },
    async onDiscard(records) {
      await this.discard({
        dataset: this.dataset,
        records: records,
      });
    },
    async onValidate(records) {
      const filteredRecord = records.filter(
        (r) => r.currentAnnotation || r.predicted_as || r.multi_label
      );
      const validatedRecords = filteredRecord.map((record) => {
        const annotationLabels = record.currentAnnotation?.labels || null;
        const modelPredictionLabels = this.formatLabels(record.predicted_as);
        const labelsForValidate =
          annotationLabels || modelPredictionLabels || [];
        return {
          ...record,
          currentAnnotation: null,
          annotation: {
            labels: labelsForValidate,
          },
        };
      });

      await this.validate({
        dataset: this.dataset,
        agent: this.$auth.user.username,
        records: validatedRecords,
      });
    },
    async onClear(records) {
      const clearedRecords = records.map((record) => {
        return {
          ...record,
          currentAnnotation: null,
          annotation: null,
          selected: true,
          status: "Edited",
        };
      });
      this.updateRecords({
        dataset: this.dataset,
        records: clearedRecords,
      });
    },
    async onReset(records) {
      const restartedRecords = records.map((record) => {
        return {
          ...record,
          currentAnnotation: record.annotation,
        };
      });
      this.resetRecords({
        dataset: this.dataset,
        records: restartedRecords,
      });
    },
    async onNewLabel(newLabel) {
      await this.dataset.$dispatch("setLabels", {
        dataset: this.dataset,
        labels: [...new Set([...this.dataset.labels, newLabel])],
      });
    },
    searchRecords(query) {
      this.$emit("search-records", query);
    },
    formatLabels(labels) {
      return (
        labels?.map((label) => ({
          class: label,
          score: 1.0,
        })) || null
      );
    },
  },
};
</script>
