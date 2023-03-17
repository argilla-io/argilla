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
  <div class="record" v-if="record">
    <div class="record--left">
      <div class="record--image-area" v-if="isRecordContainsImage">
        <img :src="metadata._image_url" alt="image of the record" />
      </div>
      <record-inputs :record="record" />
      <classifier-annotation-area
        v-if="interactionsEnabled"
        :inputLabels="listOfTexts"
        :datasetName="datasetName"
        :isMultiLabel="isMultiLabel"
        :paginationSize="paginationSize"
        :record="record"
        @update-labels="updateLabels"
        @validate="validateLabels"
        @reset="resetLabels"
      />
      <classifier-exploration-area
        v-else
        :datasetName="datasetName"
        :paginationSize="paginationSize"
        :record="record"
      />
      <record-action-buttons
        v-if="interactionsEnabled"
        :actions="textClassifierActionButtons"
        @validate="toggleValidateRecord()"
        @clear="onClearAnnotations()"
        @discard="toggleDiscardRecord()"
        @reset="onReset()"
      />
    </div>

    <div v-if="!annotationEnabled" class="record__labels">
      <template v-if="record.annotation">
        <base-tag
          v-for="label in record.annotation.labels"
          :key="label.class"
          :name="label.class"
        />
      </template>
    </div>
  </div>
</template>

<script>
import { mapActions } from "vuex";
import { TextClassificationRecord } from "@/models/TextClassification";
import { getTextClassificationDatasetById } from "@/models/textClassification.queries";
import { getAllLabelsTextByDatasetId } from "@/models/globalLabel.queries";

export default {
  props: {
    isMultiLabel: {
      type: Boolean,
      default: false,
    },
    viewSettings: {
      type: Object,
      required: true,
    },
    datasetId: {
      type: Array,
      required: true,
    },
    datasetName: {
      type: String,
      required: true,
    },
    record: {
      type: TextClassificationRecord,
      required: true,
    },
    isReferenceRecord: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    metadata() {
      return this.record?.metadata ?? {};
    },
    isRecordContainsImage() {
      return "_image_url" in this.metadata;
    },
    listOfTexts() {
      return getAllLabelsTextByDatasetId(this.datasetId);
    },
    interactionsEnabled() {
      return this.annotationEnabled && !this.isReferenceRecord;
    },
    annotationEnabled() {
      return this.viewSettings.viewMode === "annotate";
    },
    labellingRulesView() {
      return this.viewSettings.viewMode === "labelling-rules";
    },
    allowValidate() {
      return (
        this.record.status !== "Validated" &&
        (this.record.currentAnnotation ||
          this.record.prediction ||
          this.isMultiLabel)
      );
    },
    paginationSize() {
      return this.viewSettings?.pagination?.size;
    },
    textClassifierActionButtons() {
      return [
        {
          id: "validate",
          name: "Validate",
          allow: this.isMultiLabel,
          active: !this.allowValidate,
        },
        {
          id: "discard",
          name: "Discard",
          allow: true,
          active: this.record.status === "Discarded",
        },
        {
          id: "clear",
          name: "Clear",
          allow: this.isMultiLabel,
          disable: !this.record.currentAnnotation?.labels?.length || false,
        },
        {
          id: "reset",
          name: "Reset",
          allow: this.isMultiLabel,
          disable: this.record.status !== "Edited",
        },
      ];
    },
  },
  methods: {
    ...mapActions({
      updateRecords: "entities/datasets/updateDatasetRecords",
      validateAnnotations: "entities/datasets/validateAnnotations",
      resetAnnotations: "entities/datasets/resetAnnotations",
      changeStatusToDefault: "entities/datasets/changeStatusToDefault",
      resetRecords: "entities/datasets/resetRecords",
    }),
    async resetLabels() {
      await this.resetAnnotations({
        dataset: this.getTextClassificationDataset(),
        records: [
          {
            ...this.record,
            currentAnnotation: null,
          },
        ],
      });
    },
    async updateLabels(labels = []) {
      await this.updateRecords({
        dataset: this.getTextClassificationDataset(),
        records: [
          {
            ...this.record,
            selected: true,
            status: "Edited",
            currentAnnotation: {
              agent: this.$auth.user.username,
              labels: this.formatLabels(labels),
            },
          },
        ],
      });
    },
    async toggleValidateRecord(labels) {
      if (this.record.status === "Validated") {
        await this.onChangeStatusToDefault();
      } else {
        await this.validateLabels(labels);
      }
    },
    async toggleDiscardRecord() {
      if (this.record.status === "Discarded") {
        await this.onChangeStatusToDefault();
      } else {
        this.onDiscard();
      }
    },
    async validateLabels(labels) {
      const selectedAnnotation = {};
      selectedAnnotation.labels =
        this.formatLabels(labels) ||
        this.record.currentAnnotation?.labels ||
        this.formatLabels(this.record.predicted_as);
      await this.validateAnnotations({
        dataset: this.getTextClassificationDataset(),
        agent: this.$auth.user.username,
        records: [
          {
            ...this.record,
            currentAnnotation: null,
            annotation: {
              ...selectedAnnotation,
            },
          },
        ],
      });
    },
    async onChangeStatusToDefault() {
      const currentRecordAndDataset = {
        dataset: this.getTextClassificationDataset(),
        records: [this.record],
      };
      await this.changeStatusToDefault(currentRecordAndDataset);
    },
    onClearAnnotations() {
      this.updateRecords({
        dataset: this.getTextClassificationDataset(),
        records: [
          {
            ...this.record,
            selected: true,
            status: "Edited",
            currentAnnotation: {
              labels: [],
            },
          },
        ],
      });
    },
    async onReset() {
      await this.resetRecords({
        dataset: this.getTextClassificationDataset(),
        records: [
          { ...this.record, currentAnnotation: this.record.annotation },
        ],
      });
    },
    onDiscard() {
      this.$emit("discard");
    },
    getTextClassificationDataset() {
      return getTextClassificationDatasetById(this.datasetId);
    },
    formatLabels(labels) {
      return labels?.map((label) => ({
        class: label,
        score: 1.0,
      }));
    },
  },
};
</script>

<style scoped lang="scss">
.record {
  display: flex;
  &--image-area {
    display: flex;
    justify-content: flex-start;
    img {
      max-width: 20em;
      max-height: 20em;
    }
  }
  &--left {
    width: 100%;
    padding: $base-space * 4 20px 20px 20px;
    .list__item--selectable & {
      padding-right: 240px;
      padding-left: $base-space * 7;
    }
  }
  &__labels {
    position: relative;
    margin-left: 2em;
    width: 300px;
    display: block;
    height: 100%;
    overflow: auto;
    text-align: right;
    padding: 1em 1.4em 1em 1em;
    @extend %hide-scrollbar;
  }
}
</style>
