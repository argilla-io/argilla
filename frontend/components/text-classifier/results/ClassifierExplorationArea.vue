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
    <label-search
      v-if="labels.length >= shownLabels"
      :searchText="searchText"
      @input="onSearchLabel"
    />
    <div class="predictions">
      <span v-for="label in visibleLabels" :key="label.index">
        <LabelPill
          :predicted-as="predictedAs"
          :label="label"
          :show-score="true"
        />
      </span>

      <a
        v-if="visibleLabels.length < filteredLabels.length"
        href="#"
        class="predictions__more"
        @click.prevent="expandLabels()"
        >+{{ filteredLabels.length - visibleLabels.length }}</a
      >
      <a
        v-else-if="visibleLabels.length > maxVisibleLabels"
        href="#"
        class="predictions__more"
        @click.prevent="collapseLabels()"
        >Show less</a
      >
    </div>
  </div>
</template>
<script>
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
    },
  },
  idState() {
    return {
      searchText: "",
      shownLabels: DatasetViewSettings.MAX_VISIBLE_LABELS,
    };
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
    shownLabels: {
      get: function () {
        return this.idState.shownLabels;
      },
      set: function (newValue) {
        this.idState.shownLabels = newValue;
      },
    },
    labels() {
      return this.record.prediction ? this.record.prediction.labels : [];
    },
    maxVisibleLabels() {
      return DatasetViewSettings.MAX_VISIBLE_LABELS;
    },
    filteredLabels() {
      return this.labels.filter((label) =>
        label.class.toLowerCase().match(this.searchText.toLowerCase())
      );
    },
    visibleLabels() {
      return this.filteredLabels.slice(0, this.shownLabels);
    },
    predictedAs() {
      return this.record.predicted_as;
    },
  },
  methods: {
    expandLabels() {
      this.shownLabels = this.filteredLabels.length;
    },
    collapseLabels() {
      this.shownLabels = DatasetViewSettings.MAX_VISIBLE_LABELS;
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
  @include media(">desktopLarge") {
    max-width: calc(60% + 200px);
    margin-left: 0;
  }
  &__more {
    align-self: center;
    margin: 3.5px;
    text-decoration: none;
    font-weight: 600;
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
</style>
