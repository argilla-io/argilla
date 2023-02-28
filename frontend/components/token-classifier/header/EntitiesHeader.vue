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
  <div class="container">
    <div class="entities__wrapper">
      <div v-if="numberOfLabels" class="entities__container">
        <entity-label
          v-for="(label, index) in visibleLabels"
          :label="label.text"
          :shortcut="label.shortcut"
          :key="index"
          :color="`color_${label.color_id % $entitiesMaxColors}`"
        />
        <base-button
          v-if="isCollapsable"
          class="entities__container__button secondary light small"
          @click="toggleLabelsArea"
        >
          {{ buttonText }}
        </base-button>
      </div>
    </div>
  </div>
</template>

<script>
const MAX_LABELS_TO_SHOW = 10;

export default {
  props: {
    labels: {
      type: Array,
      required: true,
    },
  },
  data: () => ({
    showExpandedList: false,
    MAX_LABELS_NUMBER: MAX_LABELS_TO_SHOW,
  }),
  computed: {
    visibleLabels() {
      const visibleLabels = this.showExpandedList
        ? this.labels
        : this.showMaxLabels(this.labels);

      return visibleLabels;
    },
    numberOfLabels() {
      return this.labels.length;
    },
    isCollapsable() {
      return this.numberOfLabels > this.MAX_LABELS_NUMBER;
    },
    buttonText() {
      return this.showExpandedList
        ? `Show less`
        : `+ ${this.numberOfLabels - this.MAX_LABELS_NUMBER}`;
    },
  },
  methods: {
    toggleLabelsArea() {
      this.showExpandedList = !this.showExpandedList;
    },
    showMaxLabels(labels) {
      return labels.slice(0, this.MAX_LABELS_NUMBER);
    },
  },
};
</script>

<style lang="scss" scoped>
.container {
  @extend %container;
  padding-top: 0;
  padding-bottom: 0;
  margin-left: 0;
  @extend %collapsable-if-metrics !optional;
}
.entities {
  &__wrapper {
    position: relative;
  }
  &__container {
    padding: 0.4em 0.5em;
    margin-bottom: $base-space * 2;
    background: palette(white);
    border-radius: $border-radius-m;
    box-shadow: $shadow-300;
    min-height: 48px;
    max-height: 189px;
    overflow: auto;
    @extend %hide-scrollbar;
    &__button {
      display: inline-block;
    }
  }
}
.entity-label {
  margin: 4px;
}
</style>
