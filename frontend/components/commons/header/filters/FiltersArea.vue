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
  <div class="filters__content">
    <div class="container">
      <div class="filters__row">
        <div class="filters__block">
          <search-bar
            class="filters__searchbar"
            :dataset="dataset"
            @submit="onTextQuerySearch"
          />
          <filters-list
            :dataset="dataset"
            @applyFilter="onApplyFilter"
            @applyMetaFilter="onApplyMetaFilter"
            @applySortBy="onApplySortBy"
            @removeAllMetadataFilters="onRemoveAllMetadataFilters"
            @removeFiltersByGroup="onRemoveFiltersByGroup"
          ></filters-list>
          <filter-similarity
            v-if="annotationEnabled"
            :filterIsActive="enableSimilaritySearch"
            @search-records="onSimilaritySearch"
          />
        </div>
        <slot />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    dataset: {
      type: Object,
      default: () => ({}),
    },
    enableSimilaritySearch: {
      type: Boolean,
      required: true,
    },
  },
  data: () => ({
    sortable: {
      type: Boolean,
      default: false,
    },
    sortBy: "gold",
    sortByDir: "desc",
    sortOptions: [
      { filter: "annotated_as", text: "Annotated as", range: ["A", "Z"] },
      { filter: "predicted_as", text: "Predicted as", range: ["A", "Z"] },
      { filter: "score", text: "Score", range: ["0", "1"] },
    ],
  }),
  computed: {
    viewMode() {
      return this.dataset.viewSettings.viewMode;
    },
    annotationEnabled() {
      return this.viewMode === "annotate";
    },
  },
  methods: {
    onTextQuerySearch(text) {
      if (text === "") {
        text = undefined;
      }
      this.$emit("search-records", { query: { text } });
    },
    onApplyFilter({ filter, values }) {
      if (Array.isArray(values) && !values.length) {
        values = undefined;
      }
      this.$emit("search-records", {
        query: {
          [filter]: values,
        },
      });
    },
    onApplyMetaFilter({ filter, values }) {
      this.$emit("search-records", {
        query: {
          metadata: {
            [filter]: values,
          },
        },
      });
    },
    async onRemoveAllMetadataFilters(filters) {
      let query = {};
      filters.forEach((f) => (query[f.key] = []));
      this.$emit("search-records", { query: { metadata: query } });
    },
    async onRemoveFiltersByGroup(filters) {
      let query = {};
      filters.forEach(
        (f) => (query[f.key] = f.key === "score" ? undefined : [])
      );
      this.$emit("search-records", { query });
    },
    async onApplySortBy(sortList) {
      this.$emit("search-records", {
        query: this.dataset.query,
        sort: sortList,
      });
    },
    onSimilaritySearch(query) {
      this.$emit("search-records", { query });
    },
  },
};
</script>

<style lang="scss" scoped>
.container {
  @extend %container;
  padding-top: 0;
  padding-bottom: 0;
  margin-left: 0;
  @extend %collapsable-if-metrics !optional;
}

.filters {
  color: $black-54;
  &__row {
    display: flex;
    align-items: center;
  }
  &__content {
    padding: $base-space * 4 0;
    position: relative;
    width: 100%;
  }
  &__block {
    display: flex;
    align-items: center;
    width: calc(100% - 300px);
  }
  &__searchbar {
    margin-right: $base-space;
    width: 100%;
    @include media(">desktop") {
      margin-right: $base-space * 2;
    }
  }
}
</style>
