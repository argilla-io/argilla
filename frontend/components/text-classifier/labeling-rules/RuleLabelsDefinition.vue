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
        <slot name="records-metric" />
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
    <p
      class="rule__info"
      v-if="
        currentRule &&
        selectedLabels.includes(currentRule.label) &&
        currentRule.description === currentRule.query
      "
    >
      {{
        saved
          ? "The rule has been saved"
          : "This query with this label is already saved as rule"
      }}.
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
      saved: false,
      searchText: "",
      selectedLabels: [],
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
        label.class.toLowerCase().match(this.searchText.toLowerCase())
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
    currentRule(n) {
      if (n) {
        this.selectedLabels = [n.label];
        this.$emit("update-labels", [n.label]);
      }
    },
    query(n) {
      this.saved = false;
      if (!n) {
        this.selectedLabels = [];
        this.$emit("update-labels", undefined);
      }
    },
  },
  mounted() {
    if (this.currentRule) {
      this.selectedLabels = this.currentRule ? [this.currentRule.label] : [];
    }
  },
  methods: {
    ...mapActions({
      changeViewMode: "entities/datasets/changeViewMode",
      defineRule: "entities/text_classification/defineRule",
      updateRule: "entities/text_classification/updateRule",
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
      this.saved = true;
      this.collapseLabels();
      this.$emit("update-rule");
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
    updateLabels(labels) {
      this.$emit("update-labels", labels);
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
    color: palette(grey, medium);
    margin-left: auto;
    margin-top: 0;
    white-space: nowrap;
    text-align: right;
    @include font-size(14px);
    margin-left: 0.5em;
    strong {
      font-weight: 600;
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
