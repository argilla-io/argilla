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
  <span>
    {{ numericValue }}<span>{{ type }}</span>
    <slot />
    <span v-if="percent">%</span>
  </span>
</template>

<script>
export default {
  props: {
    value: {
      type: Number,
      default: undefined,
    },
    type: {
      type: String,
      default: undefined,
    },
    decimals: {
      type: Number,
      default: 2,
    },
    percent: {
      type: Boolean,
      default: false,
    },
  },
  data: () => ({}),
  computed: {
    numericValue() {
      if (this.percent === true) {
        const v = this.value * 100;
        if (v % 1 === 0) {
          return v;
        }
        return v.toFixed(this.decimals);
      }
      return this.value.toFixed(this.decimals);
    },
  },
};
</script>
