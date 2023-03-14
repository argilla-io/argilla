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
      :datasetId="datasetId"
      :datasetName="datasetName"
      :datasetTask="datasetTask"
      :enableSimilaritySearch="enableSimilaritySearch"
      @search-records="searchRecords"
    />
    <global-actions
      :datasetId="datasetId"
      :datasetName="datasetName"
      :datasetTask="datasetTask"
      :datasetVisibleRecords="dataset.visibleRecords"
      :availableLabels="listOfTexts"
      :isMultiLabel="isMultiLabel"
      @discard-records="onDiscard"
      @validate-records="onValidate"
      @clear-records="onClear"
      @reset-records="onReset"
      @on-select-labels="onSelectLabels($event)"
    />
  </div>
</template>

<script>
import { mapActions } from "vuex";
import { getDatasetFromORM } from "@/models/dataset.utilities";
import {
  getAllLabelsByDatasetId,
  getAllLabelsTextByDatasetId,
} from "@/models/globalLabel.queries";
import { Notification } from "@/models/Notifications";

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
  data() {
    return {
      isSortAsc: true,
      sortBy: "order",
    };
  },
  computed: {
    dataset() {
      //TODO when refactor of filter part from header, remove this computed/and get only what is necessary as props
      return getDatasetFromORM(this.datasetId, this.datasetTask, true);
    },
    isMultiLabel() {
      return this.dataset.isMultiLabel;
    },
    labels() {
      return getAllLabelsByDatasetId(
        this.datasetId,
        this.sortBy,
        this.isSortAsc
      );
    },
    listOfTexts() {
      return getAllLabelsTextByDatasetId(
        this.datasetId,
        this.sortBy,
        this.isSortAsc
      );
    },
  },
  methods: {
    ...mapActions({
      updateRecords: "entities/datasets/updateDatasetRecords",
      discard: "entities/datasets/discardAnnotations",
      validate: "entities/datasets/validateAnnotations",
      resetRecords: "entities/datasets/resetRecords",
    }),
    async onSelectLabels({ labels, selectedRecords, labelsToRemove }) {
      const records = selectedRecords.map((record) => {
        const pendingStatusProperties = {
          selected: true,
          status: "Edited",
        };
        const currentAnnotationLabels = record.currentAnnotation?.labels ?? [];
        const labelsToSend = this.labelsFactoryBySingleOrMultiLabel(
          labels,
          labelsToRemove,
          currentAnnotationLabels
        );

        return {
          ...record,
          ...(this.isMultiLabel && pendingStatusProperties),
          currentAnnotation: {
            agent: this.$auth.user.username,
            labels: labelsToSend,
          },
        };
      });

      let message = "";
      let numberOfChars = 0;
      let typeOfNotification = "";
      try {
        if (this.isMultiLabel) {
          const updatedRecords = {
            dataset: this.dataset,
            agent: this.$auth.user.username,
            records,
          };
          await this.updateRecords(updatedRecords);
          message = `${selectedRecords.length} records are in pending`;
          numberOfChars = 25;
          typeOfNotification = "info";
        } else {
          await this.onValidate(records);
        }
      } catch (err) {
        console.log(err);
        message = "There was a problem on annotate records";
        typeOfNotification = "error";
      } finally {
        if (this.isMultiLabel) {
          Notification.dispatch("notify", {
            message,
            numberOfChars,
            type: typeOfNotification,
          });
        }
      }
    },
    labelsFactoryBySingleOrMultiLabel(
      labels,
      labelsToRemove,
      currentAnnotationLabels
    ) {
      return this.isMultiLabel
        ? this.formatLabelsForBulkAnnotation(
            labels,
            labelsToRemove,
            currentAnnotationLabels
          )
        : this.formatLabels(labels);
    },
    formatLabelsForBulkAnnotation(
      labels,
      labelsToRemove,
      currentAnnotationLabels
    ) {
      const formattedLabels = this.formatLabels(labels);

      let labelsToSend = [
        ...new Set([...formattedLabels, ...currentAnnotationLabels]),
      ];
      labelsToSend = labelsToRemove?.length
        ? labelsToSend?.filter(
            (labelObj) => !labelsToRemove.includes(labelObj.class)
          )
        : labelsToSend;

      return labelsToSend;
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

      try {
        await this.validate({
          dataset: this.dataset,
          agent: this.$auth.user.username,
          records: validatedRecords,
        });
      } catch (err) {
        console.log(err);
      }
    },
    async onClear(records) {
      const clearedRecords = records.map((record) => {
        return {
          ...record,
          currentAnnotation: {
            labels: [],
          },
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
