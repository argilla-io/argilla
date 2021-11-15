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
  <div v-if="labels.length" class="exploration-area">
    <label-search v-if="labels.length >= maxLabels" @input="onSearchLabel" />
    <div class="predictions">
      <span v-for="label in visibleLabels" :key="label.index">
        <LabelPill
          :predicted-as="predictedAs"
          :label="label"
          :show-score="true"
        />
      </span>
      <template v-if="visibleLabels.length >= maxLabels">
        <a
          v-if="visibleLabels.length !== labels.length"
          href="#"
          class="predictions__more"
          @click.prevent="showHiddenLabels()"
          >+{{ hiddenLabels.length }}</a
        >
        <a
          v-else
          href="#"
          class="predictions__more"
          @click.prevent="hideHiddenLabels()"
          >Show less</a
        >
      </template>
    </div>
  </div>
</template>
<script>
import { DatasetViewSettings } from "@/models/DatasetViewSettings";
export default {
  props: {
    record: {
      type: Object,
      required: true,
    },
  },
  data: () => ({
    searchText: undefined,
    maxLabels: DatasetViewSettings.MAX_VISIBLE_LABELS,
  }),
  computed: {
    labels() {
      return this.record.prediction ? this.record.prediction.labels : [];
    },
    filteredLabels() {
      return this.labels.filter((label) =>
        label.class.toLowerCase().match(this.searchText)
      );
    },
    visibleLabels() {
      return this.filteredLabels.slice(0, this.maxLabels);
    },
    predictedAs() {
      return this.record.predicted_as;
    },
    hiddenLabels() {
      let labels = this.filteredLabels.slice(this.maxLabels);
      return labels.filter((label) =>
        label.class.toLowerCase().match(this.searchText)
      );
    },
  },
  methods: {
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
.exploration-area {
  margin-top: 2em;
}
.predictions {
  display: flex;
  flex-wrap: wrap;
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
</style>
