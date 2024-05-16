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
    <base-button class="small clear" @click.prevent="open = !open"
      ><svgicon name="meatballs" width="14" color="#4A4A4A" />
    </base-button>
    <div v-if="open" class="extra-actions__content">
      <div @click="showRecordInfoModal()">
        <span>View record info</span>
      </div>
      <base-action-tooltip tooltip="Copied">
        <div @click="$copyToClipboard(recordClipboardText)">
          <span>Copy text</span>
        </div>
      </base-action-tooltip>
    </div>
  </div>
</template>

<script>
import "assets/icons/meatballs";
import { IdState } from "vue-virtual-scroller";

export default {
  mixins: [
    IdState({
      // You can customize this
      idProp: (vm) => `${vm.datasetName}-${vm.recordId}`,
    }),
  ],
  props: {
    recordId: {
      type: String | Number,
      required: true,
    },
    recordClipboardText: {
      type: Array | String,
      required: true,
    },
    datasetName: {
      type: String,
      required: true,
    },
  },
  idState() {
    return {
      open: false,
    };
  },
  computed: {
    open: {
      get() {
        return this.idState.open;
      },
      set(newValue) {
        this.idState.open = newValue;
      },
    },
  },
  beforeDestroy() {
    this.close();
  },
  methods: {
    showRecordInfoModal() {
      this.$emit("show-record-info-modal");
      this.close();
    },
    close() {
      this.open = false;
    },
  },
};
</script>

<style lang="scss" scoped>
.extra-actions {
  position: relative;
  &__content {
    position: absolute;
    right: 0.7em;
    top: calc(100% + $base-space);
    background: white;
    border-radius: $border-radius;
    box-shadow: $shadow;
    padding: 3px;
    min-width: 135px;
    z-index: 1;
    .disabled {
      pointer-events: none;
      opacity: 0.7;
    }
    div {
      padding: 0.5em;
      color: $black-54;
      cursor: pointer;
      display: block;
      background: white;
      transition: background 0.3s ease-in-out;
      &:first-child {
        border-top-left-radius: $border-radius;
        border-top-right-radius: $border-radius;
      }
      &:last-child {
        border-bottom-left-radius: $border-radius;
        border-bottom-right-radius: $border-radius;
      }
      &:hover {
        transition: background 0.3s ease-in-out;
        background: $black-4;
      }
    }
  }
}
</style>
