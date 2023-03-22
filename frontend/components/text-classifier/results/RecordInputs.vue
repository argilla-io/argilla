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
  <div
    ref="list"
    :class="isRecordTextExpanded ? 'record__expanded' : 'record__collapsed'"
  >
    <div :class="!explanation ? 'record__content' : ''">
      <span v-for="(text, index) in data" :key="index" class="record">
        <span :class="['record__item', isHtml(text) ? 'record--email' : '']">
          <span class="record__key">{{ index }}:</span>
          <lazy-record-explain
            v-if="explanation"
            :record="record"
            :explain="explanation[index]"
          />
          <lazy-record-string v-else :record="record" :text="text" />
        </span>
      </span>
    </div>
    <base-button
      v-if="isCollapsableRecordText"
      class="secondary text record__show-more"
      @click.prevent="showFullRecord = !showFullRecord"
      >{{ !showFullRecord ? "Full record" : "Show less" }}
    </base-button>
  </div>
</template>

<script>
export default {
  props: {
    record: {
      type: Object,
      required: true,
    },
    disabledCollapsableText: {
      type: Boolean,
      required: true,
    },
  },
  data: () => ({
    showFullRecord: false,
    scrollHeight: undefined,
  }),
  computed: {
    data() {
      const entries = Object.entries(this.record.inputs);
      entries.sort(([keyA], [keyB]) => keyA.localeCompare(keyB));

      return Object.fromEntries(entries);
    },
    explanation() {
      return this.record.explanation;
    },
    visibleRecordHeight() {
      return this.$mq === "lg" ? 468 : 260;
    },
    isCollapsableRecordText() {
      return (
        !this.disabledCollapsableText &&
        this.scrollHeight >= this.visibleRecordHeight
      );
    },
    isRecordTextExpanded() {
      return this.showFullRecord || this.disabledCollapsableText;
    },
  },
  updated() {
    this.calculateScrollHeight();
  },
  mounted() {
    this.calculateScrollHeight();
  },
  methods: {
    isHtml(record) {
      return record.includes("<meta"); // TODO: improve
    },
    calculateScrollHeight() {
      if (this.$refs.list) {
        this.scrollHeight = this.$refs.list.clientHeight;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.record {
  white-space: pre-line;
  display: block;
  &__collapsed {
    .record__content {
      max-height: 260px;
      overflow: hidden;
      @include media(">xxl") {
        max-height: 468px;
      }
    }
  }
  &__key {
    font-weight: 600;
    margin-right: 0.5em;
    text-transform: uppercase;
    @include font-size(16px);
  }
  &__item {
    margin-right: 1em;
    display: block;
    @include font-size(16px);
    line-height: 1.6em;
  }
  &--email {
    display: block;
    :deep(table) {
      width: calc(100% - 3em) !important;
      max-width: 700px !important;
      display: inline-block;
      overflow: scroll;
      td {
        min-width: 100px !important;
      }
      @include media(">xxl") {
        max-width: 1140px !important;
      }
    }
    :deep(img) {
      display: none;
    }
    :deep(pre) {
      white-space: pre-wrap !important;
    }
    :deep(.record__content) {
      display: block;
      max-width: 748px !important;
      margin-left: 0 !important;
      word-break: break-word !important;
      @include media(">xxl") {
        max-width: 1140px !important;
      }
    }
    :deep(div.WordSection1) {
      word-break: break-all !important;
      p {
        font-family: initial !important;
      }
    }
  }
}
</style>
