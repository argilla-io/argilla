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
  <ul class="metrics__list">
    <li v-for="(item, index) in sortedObject.slice(0, limit)" :key="index">
      <label class="metrics__list__name">{{ item[0] }}</label>
      <span class="metrics__list__counter">
        {{ item[1] | formatNumber }}
      </span>
    </li>
    <base-button
      v-if="limit !== 0 && sortedObject.length > 3"
      class="link small"
      @click="$emit('limit', k)"
      >{{ limit === 3 ? `Show more` : `Show less` }}</base-button
    >
  </ul>
</template>
<script>
export default {
  props: {
    limit: {
      type: Number,
      required: true,
    },
    object: {
      type: Object,
      required: true,
    },
    k: {
      type: String,
      required: true,
    },
  },
  computed: {
    sortedObject() {
      return Object.entries(this.object[this.k]).sort(([, a], [, b]) => b - a);
    },
  },
};
</script>
<style scoped lang="scss">
.button {
  margin-top: $base-space * 2;
}
</style>
