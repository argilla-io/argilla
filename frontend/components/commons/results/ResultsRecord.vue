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
        isAnnotatedView ? 'list__item--annotation-mode' : 'list__item',
        recordStatus === 'Discarded' ? 'discarded' : null,
      ]"
    >
      <base-checkbox
        v-if="isAnnotatedView"
        class="list__checkbox"
        :value="recordSelected"
        @change="onCheckboxChanged($event)"
      >
      </base-checkbox>
      <slot v-if="datasetTask !== 'TextClassification'" />
      <record-text-classification
        v-if="datasetTask === 'TextClassification'"
        :datasetLabels="datasetLabels"
        :datasetId="datasetId"
        :datasetName="datasetName"
        :recordId="recordId"
      />
      <record-extra-actions
        :key="recordId"
        :allow-change-status="isAnnotatedView"
        :recordId="recordId"
        :recordStatus="recordStatus"
        :recordClipboardText="recordClipboardText"
        :metadata="recordMetadata"
        :datasetName="datasetName"
        :task="datasetTask"
        @on-change-record-status="onChangeRecordStatus"
        @show-record-info-modal="onShowRecordInfoModal()"
      />
      <status-tag v-if="showStatusTag" :title="recordStatus"></status-tag>
    </div>
  </div>
</template>
<script>
import { mapActions } from "vuex";
import { getViewSettingsByDatasetName } from "@/models/viewSettings.queries";

export default {
  props: {
    dataset: {
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
    datasetTask: {
      type: String,
      required: true,
    },
    datasetLabels: {
      type: Array,
      default: () => [],
    },
    record: {
      type: Object,
      required: true,
    },
    recordId: {
      type: String | Number,
      required: true,
    },
    recordStatus: {
      type: String,
      required: true,
    },
    recordSelected: {
      type: Boolean,
      required: true,
    },
    recordClipboardText: {
      type: Array | String,
      required: true,
    },
    recordMetadata: {
      type: Object,
      required: true,
    },
    records: {
      type: Array,
      required: true,
    },
  },
  computed: {
    viewSettings() {
      return getViewSettingsByDatasetName(this.datasetName);
    },
    isAnnotatedView() {
      return this.viewSettings.viewMode === "annotate";
    },
    showStatusTag() {
      return this.isAnnotatedView && this.recordStatus !== "Default";
    },
  },
  methods: {
    ...mapActions({
      updateRecords: "entities/datasets/updateDatasetRecords",
      discard: "entities/datasets/discardAnnotations",
      validate: "entities/datasets/validateAnnotations",
    }),
    async onCheckboxChanged(checkboxStatus) {
      const record = this.records.find((r) => r.id === this.recordId);
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
