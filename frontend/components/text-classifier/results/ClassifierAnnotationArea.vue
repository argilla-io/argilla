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
      v-if="labels.length > maxVisibleLabels"
      :searchText="searchText"
      @input="onSearchLabel"
    />
    <div
      :class="[UXtest === 'fixed' ? 'fixed' : null, 'feedback-interactions']"
    >
      <ClassifierAnnotationButton
        v-for="label in visibleLabels"
        :id="label.class"
        :key="`${label.class}`"
        v-model="selectedLabels"
        :allow-multiple="isMultiLabel"
        :label="label"
        :class="[
          'label-button',
          predictedAs.includes(label.class) ? 'predicted-label' : null,
          UXtest === 'fixed' ? 'fixed' : null,
        ]"
        :data-title="label.class"
        :value="label.class"
        @change="updateLabels"
      >
      </ClassifierAnnotationButton>

      <a
        v-if="visibleLabels.length < filteredLabels.length"
        href="#"
        class="feedback-interactions__more"
        @click.prevent="expandLabels()"
        >+{{ filteredLabels.length - visibleLabels.length }}</a
      >
      <a
        v-else-if="visibleLabels.length > maxVisibleLabels"
        href="#"
        class="feedback-interactions__more"
        @click.prevent="collapseLabels()"
        >Show less</a
      >
    </div>
  </div>
</template>
<script>
import "assets/icons/ignore";
import { DatasetViewSettings } from "@/models/DatasetViewSettings";
import { IdState } from "vue-virtual-scroller";

export default {
  mixins: [
    IdState({
      // You can customize this
      idProp: (vm) => `${vm.dataset.name}-${vm.record.id}`,
    }),
  ],
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
  idState() {
    return {
      searchText: "",
      selectedLabels: [],
      shownLabels: DatasetViewSettings.MAX_VISIBLE_LABELS,
    };
  },
  watch: {
    annotationLabels(n, o) {
      if (n !== o) {
        this.selectedLabels = this.appliedLabels;
      }
    },
  },
  computed: {
    searchText: {
      get: function () {
        return this.idState.searchText;
      },
      set: function (newValue) {
        this.idState.searchText = newValue;
      },
    },
    selectedLabels: {
      get: function () {
        return this.idState.selectedLabels;
      },
      set: function (newValue) {
        this.idState.selectedLabels = newValue;
      },
    },
    shownLabels: {
      get: function () {
        return this.idState.shownLabels;
      },
      set: function (newValue) {
        this.idState.shownLabels = newValue;
      },
    },
    maxVisibleLabels() {
      return DatasetViewSettings.MAX_VISIBLE_LABELS;
    },
    isMultiLabel() {
      return this.dataset.isMultiLabel;
    },
    labels() {
      // Setup all record labels
      const labels = Object.assign(
        {},
        ...this.dataset.labels.map((label) => ({
          [label]: { score: 0, selected: false },
        }))
      );
      // Update info with annotated ones
      this.annotationLabels.forEach((label) => {
        labels[label.class] = {
          score: 0,
          selected: true,
        };
      });
      // Update info with predicted ones
      this.predictionLabels.forEach((label) => {
        const currentLabel = labels[label.class] || label;
        labels[label.class] = {
          ...currentLabel,
          score: label.score,
        };
      });
      // Dict -> list
      return Object.entries(labels).map(([key, value]) => {
        return {
          class: key,
          ...value,
        };
      });
    },
    sortedLabels() {
      return this.labels.slice().sort((a, b) => (a.score > b.score ? -1 : 1));
    },
    filteredLabels() {
      return this.sortedLabels.filter((label) =>
        label.class.toLowerCase().match(this.searchText.toLowerCase())
      );
    },
    visibleLabels() {
      const selectedLabels = this.filteredLabels.filter(
        (l) => l.selected
      ).length;
      const availableNonSelected =
        this.shownLabels < this.filteredLabels.length
          ? this.shownLabels - selectedLabels
          : this.shownLabels;
      let nonSelected = 0;
      return this.filteredLabels.filter((l) => {
        if (l.selected) {
          return l;
        } else {
          if (nonSelected < availableNonSelected) {
            nonSelected++;
            return l;
          }
        }
      });
    },
    annotationLabels() {
      return this.record.annotation ? this.record.annotation.labels : [];
    },
    predictionLabels() {
      return this.record.prediction ? this.record.prediction.labels : [];
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
    },
  },
  mounted() {
    this.selectedLabels = this.appliedLabels;
  },
  methods: {
    updateLabels(labels) {
      if (this.isMultiLabel || labels.length > 0) {
        this.annotate();
      } else this.resetAnnotations();
    },
    resetAnnotations() {
      this.$emit("reset", this.record);
    },
    annotate() {
      this.$emit("validate", { labels: this.selectedLabels });
    },
    expandLabels() {
      this.shownLabels = this.filteredLabels.length;
    },
    collapseLabels() {
      this.shownLabels = this.maxVisibleLabels;
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
.feedback-interactions {
  margin: 0 auto 0 auto;
  padding-right: 0;
  &:not(.fixed) {
    @include media(">desktopLarge") {
      max-width: calc(60% + 200px);
      margin-left: 0;
    }
  }
  .list__item--annotation-mode & {
    padding-right: 200px;
  }
  &__more {
    align-self: center;
    margin: 3.5px;
    text-decoration: none;
    font-weight: 500;
    font-family: $sff;
    outline: none;
    padding: 0.5em;
    border-radius: 5px;
    transition: all 0.2s ease-in-out;
    display: inline-block;
    &:hover {
      transition: all 0.2s ease-in-out;
      background: palette(grey, bg);
    }
  }
}
.label-button {
  @extend %item;
  &.fixed {
    width: 24%;
    ::v-deep .annotation-button-data__info {
      margin-right: 0 !important;
      margin-left: auto !important;
    }
  }
}
</style>
