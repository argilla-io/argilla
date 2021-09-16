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
    <span v-for="(text, index) in data" :key="index" class="record">
      <span :class="['record__item', isHtml(text) ? 'record--email' : '']">
        <span class="record__key">{{ index }}:</span>
        <LazyRecordExplain
          v-if="explanation"
          :predicted="predicted"
          :query-text="queryText"
          :explain="explanation[index]"
        />
        <LazyRecordString v-else :query-text="queryText" :text="text" />
      </span>
    </span>
  </div>
</template>

<script>
export default {
  props: {
    data: {
      type: Object,
      required: true,
    },
    queryText: {
      type: String,
    },
    predicted: {
      type: String,
      default: undefined,
    },
    explanation: {
      type: Object,
      default: () => undefined,
    },
  },
  methods: {
    isHtml(record) {
      return record.includes("<meta"); // TODO: improve
    },
  },
};
</script>

<style lang="scss" scoped>
.record {
  white-space: pre-line;
  display: block;
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
    ::v-deep table {
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
    ::v-deep img {
      display: none;
    }
    ::v-deep pre {
      white-space: pre-wrap !important;
    }
    ::v-deep .record__content {
      display: block;
      max-width: 748px !important;
      margin-left: 0 !important;
      word-break: break-word !important;
      @include media(">xxl") {
        max-width: 1140px !important;
      }
    }
    ::v-deep div.WordSection1 {
      word-break: break-all !important;
      p {
        font-family: initial !important;
      }
    }
  }
}
</style>
