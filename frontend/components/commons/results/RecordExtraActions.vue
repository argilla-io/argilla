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
  <div v-click-outside="close" :key="open" class="record__extra-actions">
    <a
      v-if="hasMetadata || allowChangeStatus"
      class="extra-actions__button"
      href="#"
      @click.prevent="open = !open"
      ><svgicon name="kebab-menu-v" width="20" height="20" color="#4A4A4A"
    /></a>
    <div v-if="open" class="extra-actions__content">
      <div v-if="hasMetadata" @click="showMetadata()">
        <span>View metadata</span>
      </div>
      <template v-if="allowChangeStatus">
        <div
          v-for="status in allowedStatusActions"
          :key="status.key"
          :class="record.status === 'Discarded' ? 'disabled' : null"
          @click="onChangeRecordStatus(status.key)"
        >
          <span>{{
            record.status === "Discarded" ? "Discarded" : status.name
          }}</span>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import { BaseRecord } from "@/models/Common";
import "assets/icons/kebab-menu-v";
import { IdState } from "vue-virtual-scroller";

export default {
  mixins: [
    IdState({
      // You can customize this
      idProp: (vm) => `${vm.dataset.name}-${vm.record.id}`,
    }),
  ],
  props: {
    allowChangeStatus: {
      type: Boolean,
      default: false,
    },
    record: {
      type: BaseRecord,
      required: true,
    },
    dataset: {
      type: Object,
    },
    task: {
      type: String,
      required: true,
    },
  },
  idState() {
    return {
      open: false,
    };
  },
  data: () => ({
    statusActions: [
      // TODO: Do we need this? Just the discard action should be allowed here
      {
        name: "Discard",
        key: "Discarded",
        class: "discard",
      },
    ],
  }),
  computed: {
    open: {
      get: function () {
        return this.idState.open;
      },
      set: function (newValue) {
        this.idState.open = newValue;
      },
    },
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
    // TODO: call vuex-actions here instead of trigger event
    onChangeRecordStatus(status) {
      if (this.record.status !== status) {
        this.$emit("onChangeRecordStatus", status, this.record);
      }
      this.close();
    },
    showMetadata() {
      this.$emit("onShowMetadata");
      this.close();
    },
    close() {
      this.open = false;
    },
  },
};
</script>

<style lang="scss" scoped>
.record {
  &__extra-actions {
    position: absolute;
    top: 1.5em;
    right: 0.9em;
  }
}
.extra-actions {
  position: relative;
  &__button {
    text-align: right;
    outline: none;
    text-decoration: none;
  }
  &__content {
    position: absolute;
    right: 0.7em;
    top: 2em;
    background: white;
    border-radius: 3px;
    box-shadow: 0 5px 11px 0 rgba(0, 0, 0, 0.5);
    padding: 3px;
    min-width: 135px;
    z-index: 1;
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
        background: palette(grey, bg);
      }
    }
  }
}
</style>
