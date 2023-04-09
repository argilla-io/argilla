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
    <div :class="isSelectableRecord ? 'list__item--selectable' : 'list__item'">
      <div class="record__header">
        <template v-if="!weakLabelingEnabled">
          <template v-if="annotationEnabled">
            <div class="record__header--left" v-if="!isReferenceRecord">
              <base-checkbox
                v-if="!isPageSizeEqualOne"
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
            data-title="Event Timestamp"
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
          :datasetName="dataset.name"
          :recordId="record.id"
          :recordClipboardText="record.clipboardText"
          @show-record-info-modal="onShowRecordInfoModal"
        />
      </div>
      <RecordTextClassification
        v-if="datasetTask === 'TextClassification'"
        :viewSettings="viewSettings"
        :isMultiLabel="dataset.isMultiLabel"
        :datasetId="datasetId"
        :datasetName="dataset.name"
        :record="record"
        :isReferenceRecord="isReferenceRecord"
        @discard="onDiscard()"
      />
      <RecordText2Text
        v-if="datasetTask === 'Text2Text'"
        :viewSettings="viewSettings"
        :datasetId="datasetId"
        :datasetName="dataset.name"
        :record="record"
        :isReferenceRecord="isReferenceRecord"
        @discard="onDiscard()"
      />
      <RecordTokenClassification
        v-if="datasetTask === 'TokenClassification'"
        :datasetId="datasetId"
        :datasetName="dataset.name"
        :datasetQuery="dataset.query"
        :datasetLastSelectedEntity="dataset.lastSelectedEntity"
        :viewSettings="viewSettings"
        :record="record"
        :isReferenceRecord="isReferenceRecord"
        @discard="onDiscard()"
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
import { getDatasetFromORM } from "@/models/dataset.utilities";
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
      return getDatasetFromORM(this.datasetId, this.datasetTask);
    },
    viewSettings() {
      return getViewSettingsWithPaginationByDatasetName(this.dataset.name);
    },
    isSelectableRecord() {
      return this.annotationEnabled && !this.isPageSizeEqualOne;
    },
    isPageSizeEqualOne() {
      return this.viewSettings.pagination.size === 1;
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
    }),
    async onCheckboxChanged(checkboxStatus, id) {
      const record = this.visibleRecords.find((r) => r.id === id);
      await this.updateRecords({
        dataset: this.dataset,
        records: [{ ...record, selected: checkboxStatus }],
        // TODO: update annotation status if proceed
      });
    },
    async onDiscard() {
      await this.discard({
        dataset: this.dataset,
        records: [this.record],
      });
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
      gap: 20px;
      align-items: center;
      margin-right: auto;
      margin-left: 20px;
      .list__item--selectable & {
        margin-left: $base-space * 2;
      }
    }
  }
  &__extra-actions {
    margin-right: $base-space * 2;
    margin-left: calc($base-space / 2);
  }
  &__date {
    @include font-size(12px);
    color: $black-37;
    font-weight: 500;
    margin-right: 12px;
    &[data-title] {
      position: relative;
      @extend %has-tooltip--bottom;
    }
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
  &__item {
    position: relative;
    display: inline-block;
    background: palette(white);
    border-radius: $border-radius-m;
    width: 100%;
    border: 1px solid palette(grey, 600);
    margin-top: $base-space-between-records;
    &--selectable {
      @extend .list__item !optional;
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
