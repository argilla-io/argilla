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
  <div class="wrapper">
    <div v-if="numberOfLabels" class="wrapper-labels">
      <entity-label
        v-for="{ text, shortcut, id, color_id } in filteredLabels"
        :label="text"
        :shortcut="shortcut"
        :key="id"
        :color="`color_${color_id % $entitiesMaxColors}`"
      />
      <BaseButton
        v-if="showLessMoreButton"
        class="secondary text"
        @on-click="$emit('on-toggle-show-less-more-labels')"
      >
        {{ titleShowLessMoreButton }}
      </BaseButton>
    </div>
  </div>
</template>

<script>
import { PROPERTIES } from "./editionLabel.properties";

export default {
  name: "TokenClassificationGlobalLabelsComponent",
  props: {
    labels: {
      type: Array,
      required: true,
    },
    showAllLabels: {
      type: Boolean,
      default: () => true,
    },
  },
  computed: {
    numberOfLabels() {
      return this.labels.length;
    },
    diffNumberOfLabelAndMax() {
      return this.numberOfLabels - PROPERTIES.MAX_LABELS_TO_SHOW;
    },
    isDiffInferiorOrEqualToOffset() {
      return Math.abs(this.diffNumberOfLabelAndMax) <= PROPERTIES.OFFSET;
    },
    maxNumberOfLabelToShow() {
      if (this.showAllLabels || this.isDiffInferiorOrEqualToOffset)
        return this.numberOfLabels;
      return PROPERTIES.MAX_LABELS_TO_SHOW;
    },
    showLessMoreButton() {
      return (
        this.numberOfLabels > PROPERTIES.MAX_LABELS_TO_SHOW &&
        !this.isDiffInferiorOrEqualToOffset
      );
    },
    filteredLabels() {
      return this.labels.filter(
        (label, index) => index < this.maxNumberOfLabelToShow
      );
    },
    titleShowLessMoreButton() {
      if (this.showAllLabels) {
        return `Show less`;
      }
      return `+${this.numberOfLabels - PROPERTIES.MAX_LABELS_TO_SHOW}`;
    },
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.wrapper-labels {
  @extend %hide-scrollbar;
  display: flex;
  flex-wrap: wrap;
  flex-direction: row;
  align-items: center;
  gap: 8px;
  background: transparent;
}
</style>
