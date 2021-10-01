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
  <span class="record__scroll__container">
    <span
      ref="list"
      :class="[
        'record__scroll--large',
        !allowScroll ? 'record__scroll--prevent' : '',
      ]"
    >
      <re-button
        v-if="scrollHeight >= 800"
        :title="allowScroll ? 'prevent scroll' : 'allow scroll'"
        class="record__scroll__button button-icon"
        @click="allowScroll = !allowScroll"
      >
        <svgicon
          :name="allowScroll ? 'unlock' : 'lock'"
          width="15"
          height="14"
        ></svgicon>
      </re-button>

      <span class="record__content" v-html="$highlightSearch(queryText, text)">
      </span>
    </span>
  </span>
</template>
<script>
import "assets/icons/lock";
import "assets/icons/unlock";

export default {
  props: {
    text: {
      type: [String, Array],
      required: true,
    },
    queryText: {
      type: String,
      default: undefined,
    },
  },
  data: () => ({
    allowScroll: false,
    scrollHeight: undefined,
  }),
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
<style lang="scss">
.highlight-text {
  display: inline-block;
  // font-weight: 600;
  background: #ffbf00;
  line-height: 16px;
}
</style>
<style lang="scss" scoped>
.record {
  &__scroll {
    display: block;
    max-height: 300px;
    overflow: auto;
    border: 1px solid $line-smooth-color;
    @include font-size(14px);
    margin-bottom: 0.5em;
    &--large {
      display: block;
      overflow: auto;
      max-height: 800px;
      margin-bottom: 0.5em;
      ::v-deep .record__scroll__button {
        right: 0;
        top: 0;
        .svg-icon {
          margin-left: auto !important;
        }
      }
    }
    &__container {
      position: relative;
      display: block;
    }
    &__button {
      position: absolute;
      top: 10px;
      right: 10px;
      display: block;
      background: $lighter-color;
      border: 1px solid $primary-color;
      border-radius: 3px;
      height: 25px;
      width: 25px;
      padding: 0;
      display: flex;
      align-items: center;
      .svg-icon {
        margin: auto;
        fill: $primary-color;
      }
    }
    &--prevent {
      overflow: hidden;
    }
  }
  &__content {
    word-break: break-word;
    margin-right: 200px;
    display: block;
    color: palette(grey, medium);
  }
}
</style>
