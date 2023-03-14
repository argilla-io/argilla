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
  <div class="rule-labels-definition">
    <div class="rule-labels-definition__info">
      <p class="rule__description">{{ query }}</p>
      <p class="rule__records">
        Records:
        <strong>{{ coveredRecords }}</strong>
        <svgicon
          class="rule__records__info"
          v-if="areFiltersApplied.length"
          name="info"
          width="18"
          height="18"
        />
        <span
          class="rule__records__tooltip"
          data-title="Filters are not part of the rule, but are applied to the record list below"
        />
      </p>
    </div>
    <div class="rule__labels" v-if="labels.length">
      <label-search
        v-if="labels.length > maxVisibleLabels"
        :search-text="searchText"
        @input="onSearchLabel"
      />
      <classifier-annotation-button
        v-for="label in visibleLabels"
        :id="label.class"
        :key="`${label.class}`"
        v-model="selectedLabelsVModel"
        :allow-multiple="dataset.isMultiLabel"
        :label="label"
        class="label-button"
        :data-title="label.class"
        :value="label.class"
      >
      </classifier-annotation-button>

      <base-button
        v-if="visibleLabels.length < filteredLabels.length"
        class="feedback-interactions__more secondary text"
        @click="expandLabels"
        >+{{ filteredLabels.length - visibleLabels.length }}</base-button
      >
      <base-button
        v-else-if="visibleLabels.length > maxVisibleLabels"
        class="feedback-interactions__more secondary text"
        @click="collapseLabels"
        >Show less</base-button
      >
    </div>
    <div v-else>
      <BaseFeedbackComponent
        :feedbackInput="inputForFeedbackComponent"
        @on-click="goToSettings"
        class="feedback-area"
      />
      <p class="help-message">
        {{ messageNotLabels }}
      </p>
    </div>
    <p class="rule__info" v-if="ruleInfo">{{ ruleInfo }}</p>
    <base-button
      v-else
      :disabled="!selectedLabelsVModel.length"
      class="feedback-interactions__button primary"
      @click="saveRule"
    >
      Save rule</base-button
    >
  </div>
</template>
<script>
import { mapActions } from "vuex";
import { DatasetViewSettings } from "@/models/DatasetViewSettings";
import { TextClassificationDataset } from "@/models/TextClassification";
import _ from "lodash";
import "assets/icons/info";

export default {
  props: {
    dataset: {
      type: TextClassificationDataset,
      required: true,
    },
    isSaved: {
      type: Boolean,
      default: false,
    },
  },
  data: () => {
    return {
      searchText: "",
      shownLabels: DatasetViewSettings.MAX_VISIBLE_LABELS,
      selectedLabelsVModel: [],
      inputForFeedbackComponent: {
        message: "Action needed: Create labels in the dataset settings",
        buttonLabels: [{ label: "Create labels", value: "CREATE_LABELS" }],
        feedbackType: "ERROR",
      },
      messageNotLabels:
        "To create new rules, you need al least two labels. We highly recommended starting by annotating some records with these labels.",
    };
  },
  computed: {
    areFiltersApplied() {
      const appliedFilters = Object.keys(this.dataset.query)
        .filter((f) => f !== "text")
        .map((key) => this.dataset.query[key]);
      return appliedFilters.filter((v) => v && Object.values(v).length);
    },
    currentRule() {
      return this.dataset.getCurrentLabelingRule();
    },

    currentRuleMetrics() {
      return this.dataset.getCurrentLabelingRuleMetrics() || {};
    },

    selectedLabels() {
      if (this.selectedLabelsVModel.length) {
        return this.selectedLabelsVModel;
      }
    },

    ruleInfo() {
      // TODO: We can improve this
      const storedRule =
        this.currentRule &&
        this.dataset.findRuleByQuery(this.currentRule.query);
      const storedRuleLabels = storedRule && storedRule.labels;
      const queryWithLabelsIsStored = _.isEqual(
        _.sortBy(storedRuleLabels),
        _.sortBy(this.selectedLabels)
      );
      if (this.isSaved) {
        return "The rule was saved";
      }
      if (this.selectedLabels && queryWithLabelsIsStored) {
        return `This query with ${
          this.selectedLabels.length > 1 ? "these labels" : "this label"
        } is already saved as rule`;
      }
    },
    coveredRecords() {
      return isNaN(this.currentRuleMetrics.records)
        ? "-"
        : this.$options.filters.formatNumber(this.currentRuleMetrics.records);
    },
    maxVisibleLabels() {
      return DatasetViewSettings.MAX_VISIBLE_LABELS;
    },
    query() {
      return this.dataset.query.text;
    },
    labels() {
      return this.dataset.labels.map((l) => ({ class: l, selected: false }));
    },
    filteredLabels() {
      return this.labels.filter((label) =>
        label.class.toLowerCase().match(this.searchText.toLowerCase())
      );
    },
    visibleLabels() {
      const selectedLabelsVModel = this.filteredLabels.filter((l) =>
        this.selectedLabelsVModel.includes(l.class)
      ).length;
      const availableNonSelected =
        this.shownLabels < this.filteredLabels.length
          ? this.shownLabels - selectedLabelsVModel
          : this.shownLabels;
      let nonSelected = 0;
      return this.filteredLabels.filter((l) => {
        if (this.selectedLabelsVModel.includes(l.class)) {
          return l;
        } else {
          if (nonSelected < availableNonSelected) {
            nonSelected++;
            return l;
          }
        }
      });
    },
    datasetName() {
      return this.$route.params.dataset;
    },
    datasetWorkspace() {
      return this.$route.params.workspace;
    },
  },
  watch: {
    selectedLabels: {
      handler: function (newValue) {
        if (!_.isEqual(_.sortBy(newValue), _.sortBy(this.currentRule.labels))) {
          // Here send description too --> update Rule
          this.$emit("update-rule", {
            query: this.query,
            labels: newValue,
          });
        }
      },
      deep: true,
    },
    currentRule(newValue) {
      if (newValue && newValue.labels) {
        this.selectedLabelsVModel = [...newValue.labels];
      }
    },
  },
  methods: {
    ...mapActions({
      changeViewMode: "entities/datasets/changeViewMode",
    }),
    saveRule() {
      this.collapseLabels();
      this.$emit("save-rule", {
        query: this.currentRule.query,
        labels: this.selectedLabels,
      });
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
    async changeToAnnotationViewMode() {
      await this.changeViewMode({
        dataset: this.dataset,
        value: "annotate",
      });
    },
    goToSettings() {
      this.$router.push({
        name: "datasets-workspace-dataset-settings",
        params: {
          dataset: this.datasetName,
          workspace: this.datasetWorkspace,
        },
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
.rule-labels-definition {
  height: 100%;
  display: flex;
  flex-flow: column;
  &__info {
    display: flex;
  }
}
.feedback-interactions {
  .list__item--selectable & {
    padding-right: 200px;
  }
  &__more {
    margin: 3.5px;
    display: inline-block;
  }
  &__button {
    margin-top: auto;
    margin-bottom: 0 !important;
    align-self: flex-start;
  }
}
.label-button {
  @extend %item;
}
.help-message {
  color: $black-37;
  max-width: 480px;
}
.label-button {
  margin: 5px;
}
.label-button :deep(.button) {
  justify-content: center;
}
.label-button:not(.active) :deep(.button) {
  background: #e0e1ff;
}
.rule {
  &__description {
    @include font-size(18px);
    width: 100%;
    height: 20px;
    color: $brand-primary-color;
    font-weight: 600;
    margin-top: 0;
    padding: 0;
  }
  &__info {
    margin-bottom: 0;
    margin-top: auto;
    color: $black-54;
  }
  &__records {
    margin-left: auto;
    margin-top: 0;
    white-space: nowrap;
    text-align: right;
    @include font-size(14px);
    margin-left: 0.5em;
    position: relative;
    line-height: 1em;
    display: flex;
    align-items: center;
    color: $black-37;
    strong {
      font-weight: 600;
      margin-left: 0.2em;
      color: $black-54;
    }
    &__info {
      min-width: 18px;
      margin-left: 0.3em;
      fill: $black-87;
      cursor: pointer;
      &:hover {
        & + .rule__records__tooltip:after,
        & + .rule__records__tooltip:before {
          display: block;
          opacity: 1;
          z-index: 1;
          width: auto;
          height: auto;
          overflow: visible;
        }
      }
    }
    &__tooltip {
      position: absolute;
      right: 7px;
      height: $base-space * 2;
      @extend %has-tooltip--bottom;
      @extend %tooltip-large-text;
    }
  }
  &__labels {
    margin-bottom: 1em;
    margin-left: -5px;
    margin-right: -5px;
  }
}
.searchbar {
  margin-top: 0 !important;
  margin-left: 5px !important;
}
</style>
