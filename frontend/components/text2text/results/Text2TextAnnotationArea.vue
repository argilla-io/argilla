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
    <div v-if="annotation.length">
      <text-2-text-list :list="annotation" :editable="true" @annotate="onAnnotate" />
    </div>
    <div v-else-if="prediction.length">
      <text-2-text-list :list="prediction" :editable="true" @annotate="onAnnotate" />
    </div>
    <div v-else>
      <text-2-text-list :list="[]" :editable="true" @annotate="onAnnotate" />
    </div>
  </div>
</template>
<script>
export default {
  props: {
    annotation: {
      type: Array,
      required: true,
    },
    prediction: {
      type: Array,
      required: true,
    },
  },
  data: () => ({
  }),
  methods: {
    onAnnotate(annotation) {
      this.$emit("annotate", annotation);
    },
  },
};
</script>
<style lang="scss" scoped>
</style>
