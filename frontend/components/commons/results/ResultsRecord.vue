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
  <div>
    <div
      :class="[
        isRecordReferenceForSimilarity
          ? 'list__item--similarity-record-reference'
          : null,
        annotationEnabled ? 'list__item--annotation-mode' : 'list__item',
        item.status === 'Discarded' ? 'discarded' : null,
      ]"
    >
      <div class="record__header">
        <template v-if="annotationEnabled">
          <div class="record__header--left">
            <base-checkbox
              class="list__checkbox"
              :value="item.selected"
              @change="onCheckboxChanged($event, item.id)"
            ></base-checkbox>
            <status-tag
              v-if="item.status !== 'Default'"
              :title="item.status"
            ></status-tag>
          </div>
          <similarity-search-component
            class="record__similarity-search"
            v-if="formattedVectors.length"
            :vectors="formattedVectors"
            @search-records="searchRecords"
          />
        </template>
        <record-extra-actions
          :key="item.id"
          :allow-change-status="annotationEnabled"
          :record="item"
          :dataset="dataset"
          :task="dataset.task"
          @onChangeRecordStatus="onChangeRecordStatus"
          @onShowMetadata="onShowMetadata(item)"
        />
      </div>
      <slot :record="item" />
    </div>
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
    item: {
      type: Object,
      required: true,
    },
  },
  computed: {
    annotationEnabled() {
      return this.dataset.viewSettings.viewMode === "annotate";
    },
    visibleRecords() {
      return this.dataset.visibleRecords;
    },
    formattedVectors() {
      // TODO get vectors correctly
      return (
        Object.keys(this.item.vectors)?.map((vector) => ({
          id: vector,
          name: vector,
          value: this.item.vectors[vector].value,
        })) || []
      );
    },
    isRecordReferenceForSimilarity() {
      // TODO compare record reference id and current id
      return false;
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

    async onChangeRecordStatus(status, record) {
      switch (status) {
        case "Validated":
          await this.validate({
            dataset: this.dataset,
            records: [record],
          });
          break;
        case "Discarded":
          await this.discard({
            dataset: this.dataset,
            records: [record],
          });
          break;
        default:
          console.warn("waT?", status);
      }
    },
    onShowMetadata(record) {
      this.$emit("show-metadata", record);
    },
    searchRecords(query) {
      this.$emit("search-records", query);
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
  &__similarity-search {
    margin-left: auto;
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
    &--similarity-record-reference {
      border: 1px solid $record-reference-border-color;
      background: $record-reference-background-color;
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
