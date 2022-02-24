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
    >
      <records-counter :total="dataset.results.total"></records-counter>
    </filters-area>
    <explain-help-info v-if="isExplainedRecord" :dataset="dataset" />
    <global-actions :dataset="dataset">
      <validate-discard-action
        :dataset="dataset"
        @discard-records="onDiscard"
        @validate-records="onValidate"
      >
        <template slot="first" slot-scope="validateDiscard">
          <annotation-label-selector
            :class="'validate-discard-actions__select'"
            :multi-label="isMultiLabel"
            :options="availableLabels"
            @selected="onSelectLabels($event, validateDiscard.selectedRecords)"
          />
        </template>
      </validate-discard-action>
      <create-new-action @new-label="onNewLabel" />
    </global-actions>
  </div>
</template>
<script>
import { mapActions } from "vuex";
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  computed: {
    isExplainedRecord() {
      return this.dataset.results.records.some((record) => record.explanation);
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
    viewMode() {
      return this.dataset.viewSettings.viewMode;
    },
  },
  methods: {
    ...mapActions({
      updateRecords: "entities/datasets/updateRecords",
      discard: "entities/datasets/discardAnnotations",
      validate: "entities/datasets/validateAnnotations",
    }),
    async onSelectLabels(labels, selectedRecords) {
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
      await this.dataset.$dispatch("setLabels", {
        dataset: this.dataset,
        labels: [...new Set([...this.dataset.labels, newLabel])],
      });
    },
  },
};
</script>
<style lang="scss" scoped></style>
