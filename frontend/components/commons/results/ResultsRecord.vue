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
        annotationEnabled ? 'list__item--annotation-mode' : 'list__item',
        item.status === 'Discarded' ? 'discarded' : null,
      ]"
    >
      <base-checkbox
        v-if="annotationEnabled"
        class="list__checkbox"
        :value="item.selected"
        @change="onCheckboxChanged($event, item.id)"
      ></base-checkbox>
      <slot :record="item" />
      <record-extra-actions
        :key="item.id"
        :allow-change-status="annotationEnabled"
        :record="item"
        :dataset="dataset"
        :task="dataset.task"
        @onChangeRecordStatus="onChangeRecordStatus"
        @show-record-info-modal="onShowRecordInfoModal(item)"
      />
      <status-tag
        v-if="annotationEnabled && item.status !== 'Default'"
        :title="item.status"
      ></status-tag>
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
    onShowRecordInfoModal(record) {
      this.$emit("show-record-info-modal", record);
    },
  },
};
</script>
<style lang="scss" scoped>
.list {
  &__checkbox.re-checkbox {
    position: absolute;
    left: $base-space * 2;
    top: $base-space * 2;
    margin: 0;
    width: auto;
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
