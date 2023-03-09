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
    <div
      v-if="numberOfLabels"
      ref="wrapperLabels"
      class="wrapper-labels"
      :class="[showAllLabels || 'show-less-labels']"
      :style="cssVars"
    >
      <entity-label
        v-for="(label, index) in labels"
        :label="label.text"
        :shortcut="label.shortcut"
        :key="index"
        :color="`color_${label.color_id % $entitiesMaxColors}`"
      />
    </div>
    <div class="button-area">
      <BaseButton
        v-if="showLessMoreButton"
        class="primary"
        @on-click="$emit('on-toggle-show-less-more-labels')"
      >
        {{ titleShowLessMoreButton }}
      </BaseButton>
    </div>
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
    showAllLabels: {
      type: Boolean,
      default: () => true,
    },
  },
  data() {
    return {
      wrapperHeight: 0,
      heightLimit: 170,
    };
  },
  mounted() {
    this.calculateHeight();
  },
  computed: {
    numberOfLabels() {
      return this.labels.length;
    },
    isCollapsable() {
      return this.numberOfLabels > this.MAX_LABELS_NUMBER;
    },
    showLessMoreButton() {
      return this.wrapperHeight >= this.heightLimit;
    },
    titleShowLessMoreButton() {
      if (this.showAllLabels) {
        return `Show Less`;
      }
      return `Show more`;
    },
    cssVars() {
      return { "--wrapper-height-limit": `${this.heightLimit}px` };
    },
  },
  watch: {
    labels() {
      this.calculateHeight();
    },
  },
  methods: {
    calculateHeight() {
      this.wrapperHeight = this.$refs.wrapperLabels?.clientHeight;
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
  gap: 8px;
  max-width: 600px;
  // scroll-behavior: auto;
  background: transparent;
}

.show-less-labels {
  max-height: var(--wrapper-height-limit);
  overflow: hidden;
}
</style>

[ "LOC", "MISC", "PER", "ORG", "patati", "patata", "LOCa", "MISCa", "PERa",
"ORGa", "patatia", "patataa", "ORGo", "patatio", "patatao", "youhou", "haha",
"hihi", "ohoh", "azdazdazdazdazdazd", "eadfadazdzadaz", "zefzefzefzefzef",
"gergerg", "hrthtrh", "dfgdfgfdg", "hfghfghfgh", "d", "azeazeaze",
"sdfsdfsdfsdf", "sdqfsqdfqsdfsdqf", ]
