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
  <div v-if="dataset && viewSettings">
    <div
      :class="[
        annotationEnabled ? 'list__item--annotation-mode' : 'list__item',
        record.status === 'Discarded' ? 'discarded' : null,
      ]"
    >
      <div class="record__header">
        <template v-if="!weakLabelingEnabled">
          <template v-if="annotationEnabled">
            <div class="record__header--left" v-if="!isReferenceRecord">
              <base-checkbox
                class="list__checkbox"
                :value="record.selected"
                @change="onCheckboxChanged($event, record.id)"
              >
              </base-checkbox>
              <status-tag
                v-if="record.status !== 'Default'"
                :title="record.status"
              />
            </div>
          </template>
          <base-date
            class="record__date"
            v-if="record.event_timestamp"
            :date="record.event_timestamp"
          />
          <similarity-search-component
            class="record__similarity-search"
            v-if="formattedVectors.length"
            :formattedVectors="formattedVectors"
            :isReferenceRecord="isReferenceRecord"
            @search-records="searchRecords"
          />
          <base-button
            v-else
            data-title="To use this function you need to have a vector associated with this record"
            class="small similarity-search__button--disabled"
          >
            Find similar
          </base-button>
        </template>
        <record-extra-actions
          :key="record.id"
          :allow-change-status="annotationEnabled && !isReferenceRecord"
          :datasetName="dataset.name"
          :recordId="record.id"
          :recordClipboardText="record.clipboardText"
          @on-change-record-status="onChangeRecordStatus"
          @show-record-info-modal="onShowRecordInfoModal()"
        />
      </div>
      <RecordTextClassification
        v-if="datasetTask === 'TextClassification'"
        :viewSettings="viewSettings"
        :isMultiLabel="dataset.isMultiLabel"
        :datasetId="datasetId"
        :datasetName="dataset.name"
        :datasetLabels="dataset.labels"
        :record="record"
        :isReferenceRecord="isReferenceRecord"
      />
      <RecordText2Text
        v-if="datasetTask === 'Text2Text'"
        :viewSettings="viewSettings"
        :datasetId="datasetId"
        :datasetName="dataset.name"
        :record="record"
        :isReferenceRecord="isReferenceRecord"
      />
      <RecordTokenClassification
        v-if="datasetTask === 'TokenClassification'"
        :datasetId="datasetId"
        :datasetName="dataset.name"
        :datasetEntities="dataset.entities"
        :datasetQuery="dataset.query"
        :datasetLastSelectedEntity="dataset.lastSelectedEntity"
        :viewSettings="viewSettings"
        :record="record"
        :isReferenceRecord="isReferenceRecord"
      />
    </div>
  </div>
</template>
<script>
import { mapActions } from "vuex";
import {
  Vector as VectorModel,
  getVectorModelPrimaryKey,
} from "@/models/Vector";
import { getTokenClassificationDatasetById } from "@/models/tokenClassification.queries";
import { getTextClassificationDatasetById } from "@/models/textClassification.queries";
import { getText2TextDatasetById } from "@/models/text2Text.queries";
import { getViewSettingsWithPaginationByDatasetName } from "@/models/viewSettings.queries";

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
    record: {
      type: Object,
      required: true,
    },
    isReferenceRecord: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    dataset() {
      return this.getDatasetFromORM();
    },
    viewSettings() {
      return getViewSettingsWithPaginationByDatasetName(this.dataset.name);
    },
    annotationEnabled() {
      return this.viewSettings.viewMode === "annotate";
    },
    weakLabelingEnabled() {
      return this.viewSettings.viewMode === "labelling-rules";
    },
    visibleRecords() {
      return this.dataset.visibleRecords;
    },
    vectors() {
      return VectorModel.query().where("record_id", this.record.id).get() || [];
    },
    formattedVectors() {
      const formattedVectors = this.vectors.map(
        ({ vector_name, dataset_id, record_id }) => {
          return {
            vectorId: getVectorModelPrimaryKey({
              vector_name,
              dataset_id,
              record_id,
            }),
            vectorName: vector_name,
          };
        }
      );
      return formattedVectors;
    },
  },
  methods: {
    ...mapActions({
      updateRecords: "entities/datasets/updateDatasetRecords",
      discard: "entities/datasets/discardAnnotations",
      validate: "entities/datasets/validateAnnotations",
    }),
    async onCheckboxChanged(checkboxStatus, id) {
      const record = this.visibleRecords.find((r) => r.id === id);
      await this.updateRecords({
        dataset: this.dataset,
        records: [{ ...record, selected: checkboxStatus }],
        // TODO: update annotation status if proceed
      });
    },
    async onChangeRecordStatus(status) {
      switch (status) {
        case "Validated":
          await this.validate({
            dataset: this.dataset,
            records: [this.record],
          });
          break;
        case "Discarded":
          await this.discard({
            dataset: this.dataset,
            records: [this.record],
          });
          break;
        default:
          console.warn(`The status ${status} is unknown`);
      }
    },
    onShowRecordInfoModal() {
      this.$emit("show-record-info-modal", this.record);
    },
    searchRecords(vector) {
      const formattedObj = this.formatSelectedVectorObj(vector);
      this.$emit("search-records", formattedObj);
    },
    formatSelectedVectorObj(vector) {
      return { query: { vector }, recordId: this.record.id, vector };
    },
    getDatasetFromORM() {
      try {
        return this.getTaskDatasetById();
      } catch (err) {
        console.error(err);
        return null;
      }
    },
    getTaskDatasetById() {
      let datasetById = null;
      switch (this.datasetTask.toUpperCase()) {
        case "TEXTCLASSIFICATION":
          datasetById = getTextClassificationDatasetById(this.datasetId);
          break;
        case "TOKENCLASSIFICATION":
          datasetById = getTokenClassificationDatasetById(this.datasetId);
          break;
        case "TEXT2TEXT":
          datasetById = getText2TextDatasetById(this.datasetId);
          break;
        default:
          throw new Error(`ERROR Unknown task: ${this.datasetTask}`);
      }
      return datasetById;
    },
  },
};
</script>
<style lang="scss" scoped>
.record {
  &__header {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    min-height: 30px;
    margin-top: 0.8em;
    &--left {
      display: flex;
      align-items: center;
      margin-right: auto;
    }
  }
  &__extra-actions {
    margin-right: $base-space;
  }
  &__date {
    @include font-size(12px);
    color: $black-37;
    font-weight: 500;
    margin-right: $base-space;
  }
}
.similarity-search {
  &__button {
    &--disabled {
      @include font-size(13px);
      font-weight: 500;
      color: $black-20;
      overflow: visible;
      cursor: default;
      &[data-title] {
        position: relative;
        @extend %has-tooltip--bottom;
        @extend %tooltip-large-text;
        &:after {
          min-width: 158px;
        }
      }
    }
  }
}
.list {
  &__checkbox.re-checkbox {
    margin: auto $base-space;
  }
  &__item {
    position: relative;
    background: palette(white);
    border-radius: $border-radius-m;
    display: inline-block;
    width: 100%;
    border: 1px solid palette(grey, 600);
    margin-bottom: $base-space-between-records;
    &--annotation-mode {
      @extend .list__item !optional;
      padding-left: $base-space;
      &.discarded {
        opacity: 0.5;
        transition: 0.3s ease-in-out;
        &:hover {
          opacity: 1;
          transition: 0.3s ease-in-out;
        }
      }
    }
  }
}
.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(-30px);
}
</style>
