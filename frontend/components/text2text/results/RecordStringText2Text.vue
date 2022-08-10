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
    :class="showFullRecord ? 'record__expanded' : 'record__collapsed'"
  >
    <span class="record__content" v-html="$highlightKeywords(text, keywords)">
    </span>
    <a
      href="#"
      v-if="scrollHeight >= visibleRecordHeight"
      class="record__button"
      @click.prevent="showFullRecord = !showFullRecord"
      >{{ !showFullRecord ? "Show full record" : "Show less" }}
    </a>
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
  data: () => ({
    showFullRecord: false,
    scrollHeight: undefined,
  }),
  computed: {
    text() {
      return this.record.text;
    },
    keywords() {
      return this.record.search_keywords;
    },
    visibleRecordHeight() {
      return this.$mq === "lg" ? 570 : 260;
    },
  },
  updated() {
    this.calculateScrollHeight();
  },
  mounted() {
    this.calculateScrollHeight();
  },
  methods: {
    calculateScrollHeight() {
      if (this.$refs.list) {
        const padding = 2;
        this.scrollHeight = this.$refs.list.clientHeight + padding;
      }
    },
  },
};
</script>
<style lang="scss" scoped>
.record {
  &__collapsed {
    .record__content {
      max-height: 260px;
      overflow: hidden;
      @include media(">xxl") {
        max-height: 570px;
      }
    }
  }
  &__content {
    word-break: break-word;
    white-space: pre-line;

    display: block;
    color: $font-medium;
    width: calc(100% - 200px);
  }
  &__button {
    display: inline-block;
    border-radius: $border-radius;
    padding: 0.5em;
    transition: all 0.2s ease;
    @include font-size(14px);
    font-weight: 400;
    background: none;
    margin-top: 1em;
    font-weight: 600;
    text-decoration: none;
    line-height: 1;
    outline: none;
    &:hover {
      transition: all 0.2s ease;
      background: palette(grey, 800);
    }
  }
}
</style>
