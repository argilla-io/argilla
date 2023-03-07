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
  <div class="validate-discard-actions">
    <base-checkbox
      v-model="allSelected"
      :disabled="!visibleRecords.length"
      class="list__item__checkbox"
    />
    <template v-if="selectedRecords.length">
      <TextClassificationBulkAnnotationSingle
        v-if="datasetTask === 'TextClassification' && !isMultiLabel"
        :class="'validate-discard-actions__select'"
        :multi-label="isMultiLabel"
        :options="availableLabels"
        @selected="onSelectLabels($event)"
      />
      <TextClassificationBulkAnnotationComponent
        v-if="datasetTask === 'TextClassification' && isMultiLabel"
        :class="'validate-discard-actions__select'"
        :datasetId="datasetId"
        :records="selectedRecords"
        :recordsIds="selectedRecordsIds"
        :labels="availableLabels"
        @on-update-annotations="onUpdateAnnotations"
      />
      <base-button
        class="clear validate-discard-actions__button"
        @click="onValidate"
        data-title="Validate"
      >
        <i
          id="validateButton"
          :key="isAnyPendingStatusRecord"
          v-badge="{
            showBadge: isAnyPendingStatusRecord,
            verticalPosition: 'top',
            horizontalPosition: 'right',
          }"
        >
          <svgicon name="validate" />
        </i>
      </base-button>
      <base-button
        class="clear validate-discard-actions__button"
        @click="onDiscard"
        data-title="Discard"
      >
        <svgicon name="discard" />
      </base-button>
      <template v-if="allowClearOrReset">
        <base-button
          class="clear validate-discard-actions__button"
          @click="onClear"
          data-title="Clear"
        >
          <svgicon name="clear" />
        </base-button>
        <base-button
          class="clear validate-discard-actions__button"
          @click="onReset"
          data-title="Reset"
        >
          <svgicon name="reset" />
        </base-button>
      </template>
      <p
        v-if="selectedRecords.length"
        class="validate-discard-actions__text"
        :class="{
          'validate-discard-actions__text_pending_record':
            isAnyPendingStatusRecord,
        }"
      >
        {{ message }}
      </p>
    </template>
  </div>
</template>

<script>
import "assets/icons/validate";
import "assets/icons/discard";
import "assets/icons/clear";
import "assets/icons/reset";
import { getDatasetFromORM } from "@/models/dataset.utilities";
import { mapActions } from "vuex";

export default {
  props: {
    datasetId: {
      type: Array,
      required: true,
    },
    datasetTask: {
      type: String,
      required: true,
    },
    visibleRecords: {
      type: Array,
      required: true,
    },
    isMultiLabel: {
      type: Boolean,
      required: true,
    },
    availableLabels: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      allSelected: false,
    };
  },
  computed: {
    dataset() {
      return getDatasetFromORM(this.datasetId, this.datasetTask);
    },
    selectedRecords() {
      // TODO: when record will be in own ORM table, replace next line by query ORM
      return this.visibleRecords.filter((record) => record.selected);
    },
    selectedPendingRecords() {
      return this.selectedRecords.filter(
        (record) => record.status === "Edited"
      );
    },
    selectedNonPendingRecords() {
      return this.selectedRecords.filter(
        (record) => record.status !== "Edited"
      );
    },
    isAnyPendingStatusRecord() {
      return this.selectedPendingRecords.length;
    },
    allowClearOrReset() {
      return (
        (this.datasetTask === "TextClassification" && this.isMultiLabel) ||
        this.datasetTask === "TokenClassification"
      );
    },
    selectedRecordsIds() {
      return new Set(
        this.selectedRecords.reduce((acc, curr) => [...acc, curr.id], [])
      );
    },
    areAllRecordsSelected() {
      return this.visibleRecords.every((record) => record.selected);
    },
    message() {
      let pendingSentence = "";
      let nonPendingSentence = "";
      const dynamicText = (number, text) => {
        return `${number} record${number === 1 ? ` is` : `s are`} ${text}`;
      };
      if (this.isAnyPendingStatusRecord) {
        pendingSentence = `${dynamicText(
          this.selectedPendingRecords.length,
          "pending validation"
        )}`;
      }
      if (this.selectedNonPendingRecords.length) {
        nonPendingSentence = `${dynamicText(
          this.selectedRecords.length,
          "selected"
        )}`;
      }
      return `${nonPendingSentence} ${
        nonPendingSentence && pendingSentence && "and "
      } ${pendingSentence}`;
    },
  },
  watch: {
    areAllRecordsSelected(newValue) {
      this.allSelected = newValue;
    },
    allSelected(allSelected) {
      if (
        allSelected ||
        this.visibleRecords.every((record) => record.selected)
      ) {
        //TODO : refactor updateRecords to pass only the datasetId instead of all dataset
        this.updateRecords({
          dataset: this.dataset,
          records: this.visibleRecords.map((record) => {
            return { ...record, selected: this.allSelected };
          }),
        });
      }
    },
  },
  methods: {
    ...mapActions({
      updateRecords: "entities/datasets/updateDatasetRecords",
    }),
    onDiscard() {
      this.$emit("discard-records", this.selectedRecords);
    },
    onClear() {
      this.$emit("clear-records", this.selectedRecords);
    },
    onReset() {
      this.$emit("reset-records", this.selectedRecords);
    },
    async onValidate() {
      this.$emit("validate-records", this.selectedRecords);
    },
    onSelectLabels(labels) {
      const { selectedRecords } = this;
      this.$emit("on-select-labels", { labels, selectedRecords });
    },
    onUpdateAnnotations(updatedAnnotations) {
      const { selectedRecords } = this;
      const labelsToAdd = this.labelsfromAnnotationsFactory(
        updatedAnnotations,
        "selected"
      );
      const labelsToRemove = this.labelsfromAnnotationsFactory(
        updatedAnnotations,
        "removed"
      );

      this.$emit("on-select-labels", {
        selectedRecords,
        labels: labelsToAdd,
        labelsToRemove: labelsToRemove,
      });
    },
    labelsfromAnnotationsFactory(annotations, paramKey) {
      return annotations.reduce(
        (accumulator, currentLabelObj) =>
          currentLabelObj[paramKey]
            ? [...accumulator, currentLabelObj.label]
            : [...accumulator],
        []
      );
    },
  },
};
</script>
<style lang="scss" scoped>
.validate-discard-actions {
  display: flex;
  gap: calc($base-space / 2);
  align-items: center;
  width: 100%;
  .re-checkbox {
    position: relative;
    left: 0;
    top: 0;
    margin: 0 $base-space 0 0;
    &:not(.checked):deep(.checkbox-container) {
      border-color: $black-20;
    }
  }
  &__select {
    margin-left: 0.8em;
    :deep(.dropdown__header) {
      cursor: pointer;
      display: flex;
      gap: $base-space * 2;
      border: none;
      padding: 5px $base-space;
      height: auto;
      .svg-icon {
        color: $black-54;
        height: 18px;
        width: 18px;
      }
      span[data-title] {
        position: relative;
        overflow: visible;
        @extend %has-tooltip--top;
      }
      &:hover {
        background: $black-4;
      }
    }
  }
  &__text {
    @include font-size(13px);
    margin: 0 $base-space;
    color: $black-54;
  }
  &__text_pending_record {
    padding: calc($base-space / 2) $base-space;
    background-color: rgb(255, 103, 95, 0.2);
    border-radius: $border-radius;
  }
  &__button {
    .svg-icon {
      color: $black-54;
      height: 18px;
      width: 18px;
    }
    &[data-title] {
      overflow: visible;
      position: relative;
      @extend %has-tooltip--top;
    }
  }
}
</style>
