<template>
  <div class="wrapper">
    <div class="container" v-for="{ id, text } in filteredLabels" :key="id">
      <div class="label-text" v-html="text" />
    </div>
    <BaseButton
      v-if="showLessMoreButton"
      class="secondary text"
      @on-click="$emit('on-toggle-show-less-more-labels')"
    >
      {{ titleShowLessMoreButton }}
    </BaseButton>
  </div>
</template>

<script>
import { PROPERTIES } from "./editionLabel.properties";

export default {
  name: "TextClassificationGlobalLabelsComponent",
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
  flex-direction: row;
  flex-wrap: wrap;
  gap: $base-space;
  scroll-behavior: auto;
  background: transparent;
  .container {
    display: flex;
  }
}

.label-text {
  outline: none;
  background: #f0f0fe;
  border-radius: 50em;
  height: 40px;
  line-height: 40px;
  padding-left: 16px;
  padding-right: 16px;
  width: 100%;
  display: flex;
  font-weight: 500;
  overflow: hidden;
  color: #4c4ea3;
  box-shadow: 0;
  transition: all 0.2s ease-in-out;
}
</style>
