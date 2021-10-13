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
  <div class="record__extra-actions" v-if="task !== 'Text2Text'">
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
  <div v-else class="record__extra-actions--text2text" v-click-outside="close">
    <a class="extra-actions__button" v-if="hasMetadata || allowChangeStatus" href="#" @click.prevent="open =! open"><svgicon name="kebab-menu-h" width="20" height="20" color="#4C4EA3" /></a>
    <div class="extra-actions__content" v-if="open">
      <div v-if="hasMetadata" @click="$emit('onShowMetadata')">
        <span>View metadata</span>
      </div>
      <template v-if="allowChangeStatus">
        <div
          :class="record.status === 'Discarded' ? 'disabled' : null"
          v-for="status in allowedStatusActions"
          :key="status.key"
          @click="onChangeRecordStatus(status.key)"
        >
          <span>{{record.status === 'Discarded' ? 'Discarded' : status.name }}</span>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import { BaseRecord } from "@/models/Common";
import "assets/icons/kebab-menu-h";

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
    task: {
      type: String,
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
    open: false,
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
    close() {
      this.open = false
    }
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
    &--text2text {
      opacity: 0;
      pointer-events: none;
      position: absolute;
      top: 1em;
      right: 2em;
    }
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
.extra-actions {
  position: relative;
  &__button {
    text-align: right;
    outline: none;
  }
  &__content {
    position: absolute;
    right: 0;
    top: 2em;
    background: white;
    border-radius: 3px;
    box-shadow: 0 5px 11px 0 rgba(0,0,0,0.50);
    padding: 3px;
    min-width: 135px;
    .disabled {
      pointer-events: none;
    }
    div {
      padding: 0.5em;
      color: $font-secondary-dark;
      cursor: pointer;
      display: block;
      border-bottom: 1px solid palette(grey, smooth);
      border-radius: 3px;
      background: white;
      transition: background 0.3s ease-in-out;
      &:last-child {
        border-bottom: none;
      }
      &:hover {
        transition: background 0.3s ease-in-out;
        background: palette(grey, smooth);
      }
    }
  }
}
</style>
