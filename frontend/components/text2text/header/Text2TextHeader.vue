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
      @discard-records="onDiscard"
      @validate-records="onValidate"
    />
  </div>
</template>

<script>
import { mapActions } from "vuex";
import { getDatasetFromORM } from "@/models/dataset.utilities";
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
  computed: {
    dataset() {
      //TODO when refactor of filter part from header, remove this computed/and get only what is necessary as props
      return getDatasetFromORM(this.datasetId, this.datasetTask, true);
    },
    allowValidation() {
      const selected = this.dataset.results.records.filter((r) => r.selected);
      return this.validationFilter(selected).length > 0;
    },
  },
  methods: {
    ...mapActions({
      discardAnnotations: "entities/datasets/discardAnnotations",
      validateAnnotations: "entities/datasets/validateAnnotations",
    }),
    validationFilter(records) {
      return records.filter(
        (r) => r.sentenceForAnnotation && r.sentenceForAnnotation.length
      );
    },
    async onDiscard(records) {
      await this.discardAnnotations({
        dataset: this.dataset,
        records: records,
      });
    },
    async onValidate(records) {
      const filteredRecords = this.validationFilter(records);
      let message = "";
      let numberOfChars = 0;
      let typeOfNotification = "";
      try {
        await this.validateAnnotations({
          dataset: this.dataset,
          agent: this.$auth.user.username,
          records: filteredRecords.map((record) => {
            return {
              ...record,
              annotation: {
                sentences: [{ text: record.sentenceForAnnotation, score: 1 }],
              },
            };
          }),
        });
        message =
          records.length > 1
            ? `${filteredRecords.length} records are validated`
            : `1 record is validated`;
        numberOfChars = 25;
        typeOfNotification = "success";
      } catch (err) {
        console.log(err);
        message = `${records.length} record(s) could not have been validated`;
        typeOfNotification = "error";
      } finally {
        Notification.dispatch("notify", {
          message,
          numberOfChars,
          type: typeOfNotification,
        });
      }
    },
    searchRecords(query) {
      this.$emit("search-records", query);
    },
  },
};
</script>
