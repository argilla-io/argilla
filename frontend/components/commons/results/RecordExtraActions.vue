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
  <div class="record__extra-actions">
    <div v-if="hasMetadata" @click="$emit('onShowMetadata')">
      <span>View metadata</span>
    </div>
    <template v-if="allowChangeStatus">
      <div
        v-for="status in allowedStatusActions"
        :key="status.key"
        @click="onChangeRecordStatus(status.key)"
      >
        <span>{{ status.name }}</span>
      </div>
    </template>
  </div>
</template>

<script>
import { BaseRecord } from "@/models/Common";

export default {
  props: {
    allowChangeStatus: {
      type: Boolean,
      default: false,
    },
    record: {
      type: BaseRecord,
      required: true,
    },
  },
  data: () => ({
    statusActions: [
      {
        name: "Discard",
        key: "Discarded",
        class: "discard",
      },
    ],
  }),
  computed: {
    hasMetadata() {
      const metadata = this.record.metadata;
      return metadata && Object.values(metadata).length;
    },
    recordStatus() {
      return this.record.status;
    },
    allowedStatusActions() {
      return this.statusActions.map((status) => ({
        ...status,
        isActive: this.recordStatus === status.key,
      }));
    },
  },
  methods: {
    onChangeRecordStatus(status) {
      if (this.record.status !== status) {
        this.$emit("onChangeRecordStatus", status, this.record);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.record {
  &__extra-actions {
    line-height: 1;
    text-align: left;
    color: $font-secondary;
    margin-top: 0.5em;
    margin-bottom: 1.5em;
    @include font-size(13px);
    padding-left: 2.3em;
    .list__item--annotation-mode & {
      padding-left: 65px;
    }
    .annotate {
      color: $success;
    }
    .discard {
      color: $error;
    }
    > div {
      margin-top: 0;
    }
    > * + *:before {
      content: "";
      margin: auto 1em;
      height: 1em;
      width: 1px;
      background: $font-medium-color;
      vertical-align: middle;
      display: inline-block;
    }
    & > * {
      display: inline-block;
      cursor: pointer;
    }
  }
}
</style>
