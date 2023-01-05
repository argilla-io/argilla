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
  <div class="record-info">
    <div class="record-info__container">
      <base-table-info
        class="record-info__table"
        :data="filteredRecordInfo"
        :columns="tableColumns"
        :global-actions="false"
        :actions="actions"
        @onActionClicked="onActionClicked"
      />
    </div>
    <div class="record-info__buttons">
      <base-button class="primary" @click="$emit('close-modal')">
        Close
      </base-button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    record: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      tableColumns: [
        {
          name: "Field Name",
          field: "name",
          type: "text",
          sortable: false,
        },
        { name: "Value", field: "value", type: "text", sortable: false },
      ],
      actions: [
        {
          name: "copy-text",
          icon: "copy",
          title: "Copy info",
          tooltip: "Copied",
        },
      ],
    };
  },
  computed: {
    recordInfo() {
      const metadataInfo =
        Object.keys(this.record.metadata).map((key) => ({
          name: `Metadata.${key}`,
          id: `metadata.${key}`,
          value: this.record.metadata[key],
        })) || [];

      const recordInfo = [
        { name: "Id", id: "id", value: this.record.id },
        {
          name: "Event_timestamp",
          id: "event_tiemstamp",
          value: this.record.event_timestamp,
        },
        {
          name: "Last_updated",
          id: "last_updated",
          value: this.record.last_updated,
        },
        { name: "Prediction", id: "prediction", value: this.record.prediction },
        { name: "Status", id: "status", value: this.record.status },
      ];
      return [...recordInfo, ...metadataInfo];
    },
    filteredRecordInfo() {
      return this.recordInfo.filter((info) => info.value);
    },
  },
  methods: {
    onActionClicked(action, info) {
      switch (action) {
        case "copy-text":
          this.$copyToClipboard(this.textToCopy(info));
          break;
        default:
          console.warn(action);
      }
    },
    textToCopy(info) {
      if (info.name.startsWith("Metadata.")) {
        return `${info.name}: ${info.value}`;
      } else if (typeof info.value === "object") {
        return JSON.stringify(info.value);
      }
      return info.value;
    },
  },
};
</script>

<style lang="scss" scoped>
.record-info {
  position: relative;
  max-width: 800px;
  margin: auto;
  pointer-events: all;
  &__container {
    overflow-y: auto;
    margin-right: -1em;
    padding-right: 1em;
    @extend %hide-scrollbar;
  }
  &__table {
    max-width: 800px;
    width: 60vw;
    margin-bottom: 0 !important;
    :deep(.table-info__item__col:first-child) {
      max-width: 200px;
      word-break: break-word;
    }
    :deep(.table-info__item__col:nth-last-of-type(-n + 1)) {
      max-width: none;
    }
    :deep(.table-info__body) {
      max-height: 40vh;
    }
  }
  &__buttons {
    display: flex;
    justify-content: flex-end;
    margin-top: 2em;
  }
}
</style>
