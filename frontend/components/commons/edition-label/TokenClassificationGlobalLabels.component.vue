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
  <div v-if="numberOfLabels" class="wrapper">
    <entity-label
      v-for="(label, index) in labels"
      :label="label.text"
      :shortcut="label.shortcut"
      :key="index"
      :color="`color_${label.color_id % $entitiesMaxColors}`"
    />
  </div>
</template>

<script>
export default {
  name: "TokenClassificationGlobalLabelsComponent",
  props: {
    labels: {
      type: Array,
      required: true,
    },
  },
  computed: {
    numberOfLabels() {
      return this.labels.length;
    },
    isCollapsable() {
      return this.numberOfLabels > this.MAX_LABELS_NUMBER;
    },
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  @extend %hide-scrollbar;
  display: flex;
  flex-wrap: wrap;
  flex-direction: row;
  gap: 8px;
  max-height: 189px;
  max-width: 600px;
  overflow: auto;
  scroll-behavior: auto;
  background: transparent;
}
</style>
