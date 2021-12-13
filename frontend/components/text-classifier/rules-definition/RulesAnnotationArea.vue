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
  <div v-if="labels.length">
    <label-search
      v-if="labels.length > maxVisibleLabels"
      :searchText="searchText"
      @input="onSearchLabel"
    />
    <ClassifierAnnotationButton
      v-for="label in visibleLabels"
      :id="label.class"
      :key="`${label.class}`"
      v-model="selectedLabels"
      :allow-multiple="isMultiLabel"
      :label="label"
      class="label-button"
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
</template>
<script>
import "assets/icons/ignore";
import { DatasetViewSettings } from "@/models/DatasetViewSettings";

export default {
  props: {
    dataset: {
      type: Object,
      required: true
    }
  },
  data: () => {
    return {
      searchText: "",
      selectedLabels: [],
      shownLabels: DatasetViewSettings.MAX_VISIBLE_LABELS
    };
  },
  computed: {
    maxVisibleLabels() {
      return DatasetViewSettings.MAX_VISIBLE_LABELS;
    },
    isMultiLabel() {
      return this.dataset.isMultiLabel;
    },
    labels() {
      return this.dataset._labels.map(l => ({ class: l }));
    },
    // sortedLabels() {
    //   return this.labels.slice().sort((a, b) => (a.score > b.score ? -1 : 1));
    // },
    filteredLabels() {
      return this.labels.filter(label =>
        label.class.toLowerCase().match(this.searchText)
      );
    },
    visibleLabels() {
      const selectedLabels = this.filteredLabels.filter(l => l.selected).length;
      const availableNonSelected =
        this.shownLabels < this.filteredLabels.length
          ? this.shownLabels - selectedLabels
          : this.shownLabels;
      let nonSelected = 0;
      return this.filteredLabels.filter(l => {
        if (l.selected) {
          return l;
        } else {
          if (nonSelected < availableNonSelected) {
            nonSelected++;
            return l;
          }
        }
      });
    }
  },
  methods: {
    updateLabels(labels) {
      console.log("selected labels :", labels);
    },
    expandLabels() {
      this.shownLabels = this.filteredLabels.length;
    },
    collapseLabels() {
      this.shownLabels = this.maxVisibleLabels;
    },
    onSearchLabel(event) {
      this.searchText = event;
    }
  }
};
</script>
<style lang="scss" scoped>
%item {
  // width: calc(25% - 5px);
  min-width: 80px;
  max-width: 238px;
}
.feedback-interactions {
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
}
</style>
