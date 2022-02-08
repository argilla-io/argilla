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
    <div v-if="isList(text)">
      <div v-for="item in text" :key="item.index">
        <span
          class="record__content"
          v-html="$highlightSearch(queryText, item)"
        >
        </span>
      </div>
    </div>

    <span
      v-else
      class="record__content"
      v-html="$highlightSearch(queryText, text)"
    >
    </span>
  </div>
</template>
<script>
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
  methods: {
    isList(record) {
      return Array.isArray(record);
    },
  },
};
</script>
<style lang="scss" scoped>
.record {
  &__content {
    word-break: break-word;
  }
}
</style>
