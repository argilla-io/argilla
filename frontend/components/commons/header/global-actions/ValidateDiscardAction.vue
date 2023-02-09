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
  <div
    class="validate-discard-actions"
    :class="[
      selectedRecords.length ? '' : 'validate-discard-actions--disabled',
    ]"
  >
    <base-checkbox
      v-model="allSelected"
      :disabled="!visibleRecords.length"
      class="list__item__checkbox"
    />
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
      :disabled="!allowValidation"
      class="primary outline small validate-discard-actions__button"
      @click="onValidate"
    >
      Validate
    </base-button>
    <base-button
      class="primary outline small validate-discard-actions__button"
      @click="onDiscard"
    >
      Discard
    </base-button>
    <p v-if="selectedRecords.length" class="validate-discard-actions__text">
      Actions will apply to the
      <span>{{ selectedRecords.length }} records</span> selected
    </p>
  </div>
</template>

<script>
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
    allowValidation: {
      type: Boolean,
      default: true,
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
    selectedRecordsIds() {
      return new Set(
        this.selectedRecords.reduce((acc, curr) => [...acc, curr.id], [])
      );
    },
  },
  watch: {
    visibleRecords(newValue) {
      this.allSelected = newValue.length
        ? newValue.every((record) => record.selected)
        : false;
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
  align-items: center;
  width: 100%;
  .re-checkbox {
    position: relative;
    left: 0;
    top: 0;
    margin: 0 $base-space 0 0;
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
  &__button {
    margin-left: $base-space;
    margin-right: $base-space;
    cursor: pointer;
    &:hover {
      border-color: $primary-color;
    }
    &:first-of-type {
      margin-right: 0;
    }
  }
  &__text {
    @include font-size(13px);
    margin: 0 $base-space;
    color: $black-54;
    span {
      font-weight: 700;
      color: $black-54;
    }
  }
  &--disabled {
    .validate-discard-actions__button,
    .validate-discard-actions__select {
      pointer-events: none;
      opacity: 0.5;
    }
  }
}
</style>
