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
  <div :class="['feedback-interactions']" class="feedback-interactions__items">
    <transition-group name="list" tag="div" >
      <ClassifierAnnotationButton
        v-for="label in sortedLabels.slice(0, maxLabelsShown)"
        :id="label.class"
        :key="`${label.class}`"
        v-model="selectedLabels"
        :allow-multiple="record.multi_label"
        :label="label"
        :class="[
          'label-button',
          selectedLabels.includes(label.class) ? 'selected' : null,
        ]"
        :data-title="label.class"
        :value="label.class"
        @change="updateLabels"
      >
      </ClassifierAnnotationButton>
    </transition-group>
    <FilterDropdown
      v-if="sortedLabels.length > maxLabelsShown"
      :visible="visible"
      class="select--label"
      :class="{ checked: false }"
      @visibility="onVisibility"
    >
      <template slot="dropdown-header">
        <span class="dropdown__text">More labels</span>
      </template>
      <template slot="dropdown-content">
        <input
          v-model="searchText"
          type="text"
          autofocus
          placeholder="Search label..."
        />
        <svgicon
          v-if="searchText != undefined"
          class="clean-search"
          name="cross"
          width="10"
          height="10"
          color="#9b9b9b"
          @click="searchText = ''"
        ></svgicon>
        <ClassifierAnnotationButton
          v-for="label in dropdownSortedLabels"
          :id="label.class"
          :key="label.class"
          v-model="selectedLabels"
          :allow-multiple="record.multi_label"
          :label="label"
          :class="['label-button']"
          :data-title="label.class"
          :value="label.class"
          @change="updateLabels"
        >
        </ClassifierAnnotationButton>
      </template>
    </FilterDropdown>
  </div>
</template>
<script>
import "assets/icons/ignore";

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
    componentLabels: undefined,
    maxLabelsShown: 12,
    selectedLabel: undefined,
    dropdownLabels: undefined,
    visible: undefined,
    selectedLabels: [],
  }),
  computed: {
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
        labelsDict[label.class] = {
          score: label.score,
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
    annotationLabels() {
      return this.record.annotation ? this.record.annotation.labels : [];
    },
    predictionLabels() {
      return this.record.prediction ? this.record.prediction.labels : [];
    },
    sortedLabels() {
      const labels = [...this.labels];
      return labels.sort((a, b) => (a.score > b.score ? -1 : 1));
    },
    dropdownSortedLabels() {
      let labels = this.sortedLabels.slice(this.maxLabelsShown);
      return labels.filter((label) =>
        label.class.toLowerCase().match(this.searchText)
      );
    },
    appliedLabels() {
      return this.labels.filter((l) => l.selected).map((label) => label.class);
    },
  },
  mounted() {
    this.selectedLabels = this.appliedLabels;
  },
  watch: {
    appliedLabels(o, n) {
      if (o.some(l => n.indexOf(l) === -1)) {
        this.selectedLabels = this.appliedLabels;
      }
    }
  },
  methods: {
    updateLabels() {
      if (this.selectedLabels.length > 0) {
        this.annotate();
      } else {
        this.$emit("edit", { labels: [] });
      }
    },
    annotate() {
      this.annotating = true;
      this.$emit("annotate", { labels: this.selectedLabels });
    },
    onVisibility(visible) {
      this.visible = visible;
    },
    decorateScore(score) {
      return score * 100;
    },
  },
};
</script>
<style lang="scss" scoped>
%item {
  width: 30%;
  min-width: 225px;
  flex-grow: 0;
  flex-shrink: 0;
  margin-left: 1% !important;
  margin-right: 1% !important;
  max-width: 238px;
}
.feedback-interactions {
  margin: 1.5em auto 0 auto;
  padding-right: 0;
  & > div {
    width: 100%;
  }
  &__items {
    display: flex;
    flex-flow: wrap;
    margin-left: -1%;
    margin-right: -1%;
  }
}
::v-deep .dropdown__header {
  border: 1px solid $line-smooth-color;
  margin: auto auto 20px auto;
  width: auto;
  height: 42px;
  line-height: 42px;
  padding-left: 0.5em;
  font-weight: 600;
}
::v-deep .dropdown__content {
  max-height: 280px;
  overflow: scroll;
}
.label-button {
  @extend %item;
}
.select--label {
  @extend %item;
  ::v-deep .--checked {
    color: $lighter-color;
    font-weight: 600;
    text-transform: none;
    display: flex;
    width: calc(100% - 1em);
    span:first-child {
      width: 112px;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    span:last-child {
      margin-left: 5px;
    }
  }
  &.active ::v-deep {
    .dropdown__header {
      background: $secondary-color;
      border: 0;
      margin: auto auto 20px auto;
      border: 1px solid $line-light-color;
      border-radius: 5px;
      transition: all 0.3s ease;
      max-width: 238px;
      &:after {
        border-color: $lighter-color;
      }
    }
  }
}
.list-item {
  display: inline-block;
  margin-right: 10px;
}
.list-enter-active,
.list-leave-active {
  transition: all 0.5s;
}
.list-enter, .list-leave-to /* .list-leave-active below version 2.1.8 */ {
  opacity: 0;
  transform: translateX(30px);
  // position: absolute !important;
  display: flex;
  justify-content: space-around;
  align-items: center;
}
</style>
