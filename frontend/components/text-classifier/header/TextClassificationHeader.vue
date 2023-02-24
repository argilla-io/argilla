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
      :isCreationLabel="allowLabelCreation"
      :isMultiLabel="isMultiLabel"
      @discard-records="onDiscard"
      @validate-records="onValidate"
      @on-select-labels="onSelectLabels($event)"
      @new-label="onNewLabel"
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
      return getAllLabelsByDatasetId(this.datasetId, "text", this.isSortAsc);
    },
    listOfTexts() {
      return getAllLabelsTextByDatasetId(
        this.datasetId,
        "text",
        this.isSortAsc
      );
    },
    allowLabelCreation() {
      return !this.dataset.settings.label_schema;
    },
  },
  methods: {
    ...mapActions({
      updateRecords: "entities/datasets/updateRecords",
      discard: "entities/datasets/discardAnnotations",
      validate: "entities/datasets/validateAnnotations",
    }),
    async onSelectLabels({ labels, selectedRecords }) {
      const records = selectedRecords.map((record) => {
        let newLabels = labels.map((label) => ({
          class: label,
          score: 1.0,
        }));
        return {
          ...record,
          annotation: {
            labels: newLabels,
          },
        };
      });
      await this.validate({
        dataset: this.dataset,
        agent: this.$auth.user.username,
        records: records,
      });
    },
    async onDiscard(records) {
      await this.discard({
        dataset: this.dataset,
        records: records,
      });
    },
    async onValidate(records) {
      const filterdRecord = records.filter(
        (r) => r.annotation || r.predicted_as || r.multi_label
      );
      await this.validate({
        dataset: this.dataset,
        agent: this.$auth.user.username,
        records: filterdRecord.map((record) => {
          let modelPrediction = {};
          modelPrediction.labels = record.predicted_as.map((pred) => ({
            class: pred,
            score: 1,
          }));
          const emptyLabels = {};
          emptyLabels.labels = [];
          return {
            ...record,
            annotation: {
              ...(record.annotation || modelPrediction || emptyLabels),
            },
          };
        }),
      });
    },
    async onNewLabel(newLabel) {
      await this.dataset.$dispatch("onSaveTokenDatasetSettings", {
        datasetId: this.datasetId,
        newLabel,
      });
    },
    searchRecords(query) {
      this.$emit("search-records", query);
    },
  },
};
</script>
