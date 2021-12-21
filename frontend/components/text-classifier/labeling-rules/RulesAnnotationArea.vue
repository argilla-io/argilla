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
  <div class="annotation-area">
    <div v-if="labels.length">
      <p v-if="!dataset.query.text">Start by entering a query in the search box</p>
      <p v-else>Select a label for your query</p>
      <label-search
        v-if="labels.length > maxVisibleLabels"
        :search-text="searchText"
        @input="onSearchLabel"
      />
      <ClassifierAnnotationButton
        v-for="label in visibleLabels"
        :id="label.class"
        :key="`${label.class}`"
        v-model="selectedLabels"
        :allow-multiple="isMultiLabel"
        :label="label"
        :class="[!dataset.query.text ? 'non-reactive' : null, 'label-button']"
        :data-title="label.class"
        :value="label.class"
        @change="updateLabel"
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
    <div v-else class="empty-labels">
      <p>This doesn't have any labels yet.</p>
      <p>
        To create new rules you need al least two labels. It's highly recommended to also annotate some records with these labels. Go to the annotation mode to 
        <a href="#" @click.prevent="changeToAnnotationViewMode">create the labels and annotate some records</a>.
      </p>
    </div>
    <rule-annotation-area-metrics :metrics="metrics" />
    <!-- <p v-if="currentRule && selectedLabels.includes(currentRule.label)">
      You have already a rule saved with that label.
    </p> -->
    <p v-if="currentRule && selectedLabels.includes(currentRule.label)">
      Rule has been saved.
    </p>
    <re-button
      v-else
      :disabled="!selectedLabels.length"
      class="feedback-interactions__button button-primary"
      @click="createRule()"
    >
      Save rule</re-button
    >
  </div>
</template>
<script>
import { mapActions } from "vuex";
import { DatasetViewSettings } from "@/models/DatasetViewSettings";

export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
    currentRule: {
      type: Object,
      default: undefined,
    },
  },
  data: () => {
    return {
      searchText: "",
      selectedLabels: [],
      metrics: {},
      shownLabels: DatasetViewSettings.MAX_VISIBLE_LABELS,
    };
  },
  computed: {
    maxVisibleLabels() {
      return DatasetViewSettings.MAX_VISIBLE_LABELS;
    },
    isMultiLabel() {
      return this.dataset.isMultiLabel;
    },
    query() {
      return this.dataset.query.text;
    },
    labels() {
      return this.dataset.labels.map((l) => ({ class: l, selected: false }));
    },
    sortedLabels() {
      return this.labels.slice().sort((a, b) => (a.score > b.score ? -1 : 1));
    },
    filteredLabels() {
      return this.sortedLabels.filter((label) =>
        label.class.toLowerCase().match(this.searchText)
      );
    },
    visibleLabels() {
      const selectedLabels = this.filteredLabels.filter((l) =>
        this.selectedLabels.includes(l.class)
      ).length;
      const availableNonSelected =
        this.shownLabels < this.filteredLabels.length
          ? this.shownLabels - selectedLabels
          : this.shownLabels;
      let nonSelected = 0;
      return this.filteredLabels.filter((l) => {
        if (this.selectedLabels.includes(l.class)) {
          return l;
        } else {
          if (nonSelected < availableNonSelected) {
            nonSelected++;
            return l;
          }
        }
      });
    },
  },
  watch: {
    async currentRule(n) {
      if (n) {
        this.selectedLabels = [n.label];
        await this.getMetricsByLabel(n.label);
      } else {
        this.selectedLabels = [];
        this.metrics = {};
      }
    },
    async query(n) {
      if (n) {
        this.selectedLabels = [];
        this.metrics = {};
      }
    }
  },
  async mounted() {
    if (this.currentRule) {
      this.selectedLabels = this.currentRule ? [this.currentRule.label] : [];
      await this.getMetricsByLabel(this.currentRule.label);
    }
  },
  methods: {
    ...mapActions({
      changeViewMode: "entities/datasets/changeViewMode",
      defineRule: "entities/text_classification/defineRule",
      updateRule: "entities/text_classification/updateRule",
      getRuleMetricsByLabel:
        "entities/text_classification/getRuleMetricsByLabel",
    }),
    async createRule() {
      if (this.currentRule) {
        await this.updateRule({
          dataset: this.dataset,
          label: this.selectedLabels[0],
        });
      } else {
        await this.defineRule({
          dataset: this.dataset,
          label: this.selectedLabels[0],
        });
      }
      this.$emit("update-rule");
    },
    async getMetricsByLabel(label) {
      if (label !== undefined && label.length) {
        const response = await this.getRuleMetricsByLabel({
          dataset: this.dataset,
          query: this.dataset.query.text,
          label: label,
        });
        this.metrics = response;
      } else {
        this.metrics = {};
      }
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
    async updateLabel(label) {
      await this.getMetricsByLabel(label);
    },
    async changeToAnnotationViewMode() {
      await this.changeViewMode({
        dataset: this.dataset,
        value: "annotate",
      });
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
  max-width: calc(100% - 200px);
  @include media(">desktopLarge") {
    max-width: 60%;
  }
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
  &__button {
    margin-top: 2em;
    margin-bottom: 0;
  }
}
.label-button {
  @extend %item;
}
.empty-labels {
  a {
    outline: none;
    color: $primary-color;
    text-decoration: none;
  }
}
</style>
