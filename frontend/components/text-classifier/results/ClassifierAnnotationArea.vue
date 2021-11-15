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
  <div v-if="labels.length" class="annotation-area">
    <label-search
      v-if="labels.length > maxLabelsShown"
      @input="onSearchLabel"
    />
    <div
      :class="['feedback-interactions']"
      class="feedback-interactions__items"
    >
      <ClassifierAnnotationButton
        v-for="label in visibleLabels"
        :id="label.class"
        :key="`${label.class}`"
        v-model="selectedLabels"
        :allow-multiple="record.multi_label"
        :label="label"
        :class="[
          'label-button',
          predictedAs.includes(label.class) ? 'predicted-label' : null,
          UXtest === 'fixed-mode' ? 'fixed-mode' : null,
        ]"
        :data-title="label.class"
        :value="label.class"
        @change="updateLabels"
      >
      </ClassifierAnnotationButton>
      <template v-if="visibleLabels.length >= maxLabelsShown">
        <a
          v-if="visibleLabels.length !== labels.length"
          href="#"
          class="feedback-interactions__more"
          @click.prevent="showHiddenLabels()"
          >+{{ hiddenLabels.length }}</a
        >
        <a
          v-else-if="visibleLabels.length > maxLabelsShown"
          href="#"
          class="feedback-interactions__more"
          @click.prevent="hideHiddenLabels()"
          >Show less</a
        >
      </template>
    </div>
  </div>
</template>
<script>
import "assets/icons/ignore";
import { DatasetViewSettings } from "@/models/DatasetViewSettings";

export default {
  props: {
    record: {
      type: Object,
      required: true,
    },
    dataset: {
      type: Object,
      required: true,
    },
  },
  data: () => ({
    searchText: undefined,
    selectedLabels: [],
    maxLabels: DatasetViewSettings.MAX_VISIBLE_LABELS,
  }),
  computed: {
    maxLabelsShown() {
      return Math.max(this.selectedLabels.length, this.maxLabels);
    },
    datasetLabels() {
      const labels = {};
      this.dataset.labels.forEach((label) => {
        labels[label] = { score: 0, selected: false };
      });
      return labels;
    },
    labels() {
      const labelsDict = { ...this.datasetLabels };
      let annotationLabels = this.annotationLabels.map((label) => {
        return {
          ...label,
          selected: true,
        };
      });

      this.predictionLabels.concat(annotationLabels).forEach((label) => {
        const predictionLabel= this.predictionLabels.find(l => l.class === label.class);
        labelsDict[label.class] = {
          score: predictionLabel ? predictionLabel.score : 0,
          selected: label.selected,
        };
      });

      return Object.keys(labelsDict).map((label) => {
        return {
          class: label,
          score: labelsDict[label].score,
          selected: labelsDict[label].selected,
        };
      });
    },
    sortedLabels() {
      return this.labels.sort((a, b) => (a.score > b.score ? -1 : 1));
    },
    filteredLabels() {
      return this.sortedLabels.filter((label) =>
        label.class.toLowerCase().match(this.searchText)
      );
    },
    visibleLabels() {
      const selected = this.filteredLabels.filter((l) => l.selected);
      let visible = this.filteredLabels.slice(0, this.maxLabelsShown);
      const selectedVisibleItems = visible.filter((l) => l.selected);
      const selectedHiddenItems = this.filteredLabels
        .slice(this.maxLabelsShown)
        .filter((l) => l.selected);
      if (selectedVisibleItems.length >= selected.length) {
        return visible;
      } else {
        visible.push(...selectedHiddenItems);
        const removeItems = visible
          .filter((l) => !l.selected)
          .splice(0, selectedHiddenItems.length);
        visible = visible.filter((item) => !removeItems.includes(item));
        return visible
      }
    },
    annotationLabels() {
      return this.record.annotation ? this.record.annotation.labels : [];
    },
    predictionLabels() {
      return this.record.prediction ? this.record.prediction.labels : [];
    },
    hiddenLabels() {
      return this.filteredLabels.slice(this.maxLabelsShown);
    },
    appliedLabels() {
      return this.filteredLabels
        .filter((l) => l.selected)
        .map((label) => label.class);
    },
    predictedAs() {
      return this.record.predicted_as;
    },
    UXtest() {
      return this.$route.query.UXtest;
    }
  },
  watch: {
    appliedLabels(o, n) {
      if (o.some((l) => n.indexOf(l) === -1)) {
        this.selectedLabels = this.appliedLabels;
      }
    },
  },
  mounted() {
    this.selectedLabels = this.appliedLabels;
  },
  methods: {
    updateLabels(labels) {
      if (this.record.multi_label || labels.length > 0) {
        this.annotate();
      } else this.resetAnnotations();
    },
    resetAnnotations() {
      this.$emit("reset", this.record);
    },
    annotate() {
      this.$emit("validate", { labels: this.selectedLabels });
    },
    showHiddenLabels() {
      this.maxLabels = this.filteredLabels.length;
    },
    hideHiddenLabels() {
      this.maxLabels = DatasetViewSettings.MAX_VISIBLE_LABELS;
    },
    onSearchLabel(event) {
      this.searchText = event;
    },
  },
};
</script>
<style lang="scss" scoped>
%item {
  // width: calc(25% - 5px);
  min-width: 80px;
  max-width: 238px;
}
.annotation-area {
  margin-top: 2em;
}
.feedback-interactions {
  margin: 0 auto 0 auto;
  padding-right: 0;
  // & > div {
  //   width: 100%;
  // }
  &__items {
    // display: flex;
    // flex-flow: wrap;
    // margin-left: -1%;
    // margin-right: -1%;
    .list__item--annotation-mode & {
      padding-right: 200px;
    }
  }
  &__more {
    align-self: center;
    margin: 2.5px;
    text-decoration: none;
    font-weight: 600;
    outline: none;
    padding: 0.5em;
    border-radius: 5px;
    transition: all 0.2s ease-in-out;
    display: inline-block;
    &:hover {
      transition: all 0.2s ease-in-out;
      background: palette(grey, smooth);
    }
  }
}
.label-button {
  @extend %item;
  &.fixed-mode {
    width: 24%;
    ::v-deep .annotation-button-data__info {
      margin-right: 0 !important;
      margin-left: auto !important;
    }
  }
}
</style>
