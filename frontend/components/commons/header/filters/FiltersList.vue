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
  <div v-click-outside="close" class="filters">
    <div class="filters__tabs">
      <p
        v-for="group in groups"
        :key="group"
        :class="{
          active: initialVisibleGroup === group || itemsAppliedOnGroup(group),
        }"
        @click="selectGroup(group)"
      >
        {{ group }}
        <span v-if="itemsAppliedOnGroup(group)"
          >({{ itemsAppliedOnGroup(group) }})</span
        >
      </p>
      <p
        class="filters__tabs__sort"
        :class="{
          active: initialVisibleGroup === 'sort' || dataset.sort.length,
        }"
        @click="selectGroup('sort')"
      >
        <svgicon name="sort" width="14" height="14" />
        Sort
        <span v-if="dataset.sort.length">({{ dataset.sort.length }})</span>
      </p>
    </div>
    <div
      v-if="initialVisibleGroup === 'sort'"
      class="filters__tabs__content filters__tabs__content--sort"
    >
      <SortList
        :sort-options="filterList"
        :sort="dataset.sort"
        @closeSort="close"
        @sortBy="onSortBy"
      />
    </div>
    <div v-for="group in groups" :key="group">
      <div
        v-if="initialVisibleGroup === group"
        :class="[
          'filters__tabs__content',
          searchableFilterList.filter((f) => f.group === group).length > 6
            ? 'filters__tabs__content--large'
            : '',
        ]"
      >
        <span
          v-for="filter in searchableFilterList.filter(
            (f) => f.group === group
          )"
          :key="filter.id"
        >
          <SelectFilter
            v-if="filter.type === 'select'"
            class="filter"
            :filter="filter"
            @apply="onApply"
          />
          <FilterScore
            v-else
            class="filter"
            :filter="filter"
            @apply="onApply"
          />
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import "assets/icons/sort";
export default {
  props: {
    dataset: {
      type: Object,
      default: () => ({}),
    },
  },
  data: () => ({
    initialVisibleGroup: undefined,
    filters: [
      {
        key: "predicted_as",
        name: "Predicted as",
        type: "select",
        group: "Predictions",
        placeholder: "Select labels",
      },
      {
        key: "predicted",
        name: "Predicted ok",
        type: "select",
        group: "Predictions",
        placeholder: "Select yes/no",
      },
      {
        key: "score",
        name: "Score",
        type: "score",
        group: "Predictions",
      },
      {
        key: "predicted_by",
        name: "Predicted by",
        type: "select",
        group: "Predictions",
        placeholder: "Select agents",
      },
      {
        key: "annotated_as",
        name: "Annotated as",
        type: "select",
        group: "Annotations",
        placeholder: "Select labels",
      },
      {
        key: "annotated_by",
        name: "Annotated by",
        type: "select",
        group: "Annotations",
        placeholder: "Select labels",
      },
      {
        key: "status",
        name: "Status",
        type: "select",
        group: "Status",
        placeholder: "Select options",
      },
    ],
  }),
  computed: {
    searchableFilterList() {
      return this.filterList.filter((f) => {
        return f.options && Object.keys(f.options).length > 0;
      });
    },
    groups() {
      return [...new Set(this.searchableFilterList.map((f) => f.group))];
    },
    isMultiLabelRecord() {
      return this.dataset.results.records.some((record) => record.multi_label);
    },
    filterList() {
      const aggregations = this.dataset.results.aggregations;
      const filters = this.filters
        .map((filter) => {
          function isZero(number) {
            return number === 0;
          }
          return {
            ...filter,
            id: filter.key,
            options: aggregations[filter.key],
            selected: this.dataset.query[filter.key],
            disabled:
              (filter.key === "score" && this.isMultiLabelRecord) ||
              !aggregations[filter.key] ||
              !Object.entries(aggregations[filter.key]).length ||
              Object.values(aggregations[filter.key]).every(isZero),
          };
        })
        .filter(({ disabled }) => !disabled);
      const metadataFilters =
        aggregations.metadata &&
        Object.keys(aggregations.metadata).map((key) => {
          const filterContent = aggregations.metadata[key];

          return {
            key: key,
            name: key,
            type: "select",
            group: "Metadata",
            placeholder: "Select options",
            id: key,
            options:
              typeof filterContent === "object" ? undefined : filterContent,
            selected: (this.dataset.query.metadata || {})[key] || [],
          };
        });
      const sortedMetadataFilters =
        (metadataFilters &&
          metadataFilters.sort((a, b) =>
            a.key.toLowerCase() > b.key.toLowerCase() ? 1 : -1
          )) ||
        [];
      return [...filters, ...sortedMetadataFilters];
    },
  },
  methods: {
    close() {
      this.initialVisibleGroup = undefined;
    },
    itemsAppliedOnGroup(group) {
      return this.filterList
        .filter((f) => f.group === group)
        .flatMap((f) => f.selected)
        .filter((f) => f).length;
    },
    selectGroup(group) {
      this.initialVisibleGroup = group;
    },
    setInitialGroup() {
      if (!this.groups.includes(this.initialVisibleGroup)) {
        this.initialVisibleGroup = this.groups[0];
      }
    },
    onApply(filter, values) {
      this.close();
      if (filter.group === "Metadata") {
        this.$emit("applyMetaFilter", { filter: filter.key, values });
      } else {
        this.$emit("applyFilter", { filter: filter.key, values });
      }
    },
    onSortBy(sortList) {
      this.close();
      this.$emit("applySortBy", sortList);
    },
  },
};
</script>

<style lang="scss" scoped>
$number-size: 18px;
.filters {
  $this: &;
  position: relative;
  display: inline-block;
  z-index: 2;
  &__tabs {
    display: flex;
    &__content {
      width: 450px;
      left: 0;
      right: 0;
      margin: auto;
      position: absolute;
      top: calc(100% + 1em);
      box-shadow: 0 5px 11px 0 rgba(0, 0, 0, 0.5);
      background: $lighter-color;
      padding: 3em 3em 2em 3em;
      border-radius: 5px;
      max-height: 550px;
      &--large {
        width: 910px;
        max-height: 80vh;
        overflow: auto;
        & > span {
          display: inline-block;
          width: 50%;
          &:nth-child(2n + 1) {
            padding-right: 1em;
          }
        }
      }
    }
    &__sort {
      svg {
        margin-right: 0.3em;
      }
    }
    p {
      cursor: pointer;
      position: relative;
      margin-bottom: 0;
      margin-top: 0;
      padding: 0.8em 1em;
      border-radius: 5px;
      margin-right: 1em;
      color: $font-secondary;
      @include font-size(15px);
      &.active {
        background: palette(grey, smooth);
        color: $primary-color;
      }
    }
  }
}

.filter {
  display: block;
  margin-bottom: 1em;
}
</style>
