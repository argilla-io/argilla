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
          width="12"
          height="12"
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
      <ClassifierAnnotationButton
        v-for="label in visibleLabels"
        :id="label.class"
        :key="`${label.class}`"
        v-model="selectedLabelsVModel"
        :allow-multiple="false"
        :label="label"
        class="label-button"
        :data-title="label.class"
        :value="label.class"
      >
      </ClassifierAnnotationButton>

      <a
        v-if="visibleLabels.length < filteredLabels.length"
        href="#"
        class="feedback-interactions__more"
        @click.prevent="expandLabels"
        >+{{ filteredLabels.length - visibleLabels.length }}</a
      >
      <a
        v-else-if="visibleLabels.length > maxVisibleLabels"
        href="#"
        class="feedback-interactions__more"
        @click.prevent="collapseLabels"
        >Show less</a
      >
    </div>
    <div v-else class="empty-labels">
      <p>This doesn't have any labels yet.</p>
      <p>
        To create new rules you need al least two labels. It's highly
        recommended to also annotate some records with these labels. Go to the
        annotation mode to
        <a href="#" @click.prevent="changeToAnnotationViewMode"
          >create the labels and annotate some records</a
        >.
      </p>
    </div>
    <p class="rule__info" v-if="ruleInfo">{{ ruleInfo }}</p>
    <re-button
      v-else
      :disabled="!selectedLabelsVModel.length"
      class="feedback-interactions__button button-primary"
      @click="saveRule"
    >
      Save rule</re-button
    >
  </div>
</template>
<script>
import { mapActions } from "vuex";
import { DatasetViewSettings } from "@/models/DatasetViewSettings";
import { TextClassificationDataset } from "@/models/TextClassification";
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

    selectedLabel() {
      if (this.selectedLabelsVModel !== undefined) {
        return this.selectedLabelsVModel[0];
      }
    },

    ruleInfo() {
      // TODO: We can improve this
      if (this.isSaved) {
        return "The rule was saved";
      }
      if (
        this.currentRule &&
        this.selectedLabelsVModel.length &&
        this.dataset.findRuleByQuery(this.currentRule.query, this.selectedLabel)
      ) {
        return "This query with this label are already saved as rule";
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
  },
  watch: {
    selectedLabel(newValue) {
      // Here send description too --> update Rule
      this.$emit("update-rule", {
        query: this.query,
        label: newValue,
      });
    },
    currentRule(newValue) {
      if (newValue && newValue.label) {
        this.selectedLabelsVModel = [newValue.label];
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
        label: this.selectedLabel,
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
  },
};
</script>
<style lang="scss" scoped>
$color: #333346;
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
    margin-top: auto;
    margin-bottom: 0 !important;
    align-self: flex-start;
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
.label-button {
  margin: 5px;
}
.label-button ::v-deep .button {
  justify-content: center;
}
.label-button:not(.active) ::v-deep .button {
  background: #e0e1ff !important;
}
.rule {
  &__description {
    @include font-size(18px);
    width: 100%;
    height: 20px;
    color: $font-secondary;
    font-weight: 600;
    margin-top: 0;
    padding: 0;
  }
  &__text {
    width: 100%;
    color: palette(grey, medium);
    @include font-size(18px);
    font-weight: 600;
    margin-top: 0;
  }
  &__info {
    margin-bottom: 0;
    margin-top: auto;
  }
  &__records {
    color: palette(grey, dark);
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
    strong {
      font-weight: 600;
      margin-left: 0.2em;
    }
    &__info {
      min-width: 12px;
      margin-left: 0.3em;
      fill: $color;
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
      right: 6px;
      @extend %hastooltip;
      &:after {
        padding: 0.5em 1em;
        top: calc(100% + 20px);
        right: 50%;
        transform: translateX(50%);
        background: $color;
        color: white;
        border: none;
        border-radius: 3px;
        @include font-size(14px);
        font-weight: 600;
        margin-bottom: 0.5em;
        min-width: 240px;
        white-space: break-spaces;
        text-align: left;
        line-height: 1.4em;
      }
      &:before {
        right: calc(50% - 7px);
        top: 13px;
        border-bottom: 7px solid $color;
        border-right: 7px solid transparent;
        border-left: 7px solid transparent;
      }
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
