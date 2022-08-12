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
  <div :class="[appliedFilters.length ? 'selected' : '', 'filter__row']">
    <svgicon
      v-if="appliedFilters.length"
      title="remove field"
      class="filter__remove-button"
      name="close"
      width="14"
      height="14"
      @click="onRemove()"
    />
    <p class="filter__label" :title="filter.name">{{ filter.name }}:</p>
    <FilterDropdown
      color-type="grey"
      :class="{ highlighted: visible || appliedFilters.length }"
      :visible="visible"
      @visibility="onVisibility"
    >
      <span slot="dropdown-header">
        <span v-if="appliedFilters.length">
          <p v-if="typeof appliedFilters === 'string'">{{ appliedFilters }}</p>
          <p
            v-for="(appliedFilter, index) in appliedFilters"
            v-else
            :key="index"
          >
            {{ appliedFilter }}
          </p>
        </span>
        <span v-else>
          {{ filter.placeholder }}
        </span>
      </span>
      <div slot="dropdown-content" v-if="visible">
        <select-options-search v-model="searchText" />
        <select-options
          ref="options"
          type="multiple"
          v-model="selectedOptions"
          :options="filterOptions(filter.options, searchText)"
          :option-name="optionName"
          :option-counter="optionCounter"
          :option-value="optionName"
        />
        <div class="filter__buttons">
          <ReButton class="primary outline" @click="onCancel">
            Cancel
          </ReButton>
          <ReButton class="primary" @click="onApply"> Filter </ReButton>
        </div>
      </div>
    </FilterDropdown>
  </div>
</template>

<script>
export default {
  props: {
    filter: {
      type: Object,
      default: () => ({}),
    },
    placeholder: {
      type: String,
      required: false,
      default: "Search...",
    },
  },
  data: () => ({
    visible: false,
    searchText: undefined,
    searchTextValue: undefined,
    selectedOptions: [],
  }),
  computed: {
    appliedFilters() {
      return this.filter.selected || [];
    },
  },
  watch: {
    appliedFilters() {
      this.updateOptions();
    },
  },
  mounted() {
    this.updateOptions();
  },
  methods: {
    updateOptions() {
      if (typeof this.appliedFilters === "string")
        this.selectedOptions = [this.appliedFilters];
      else {
        this.selectedOptions = this.appliedFilters;
      }
    },
    onVisibility(value) {
      this.visible = value;
      this.searchText = undefined;
      this.searchTextValue = undefined;
    },
    onApply() {
      this.$emit("apply", this.filter, this.selectedOptions);
      this.selectedOptions = [];
      this.visible = false;
    },
    onRemove() {
      this.$emit("apply", this.filter, []);
      this.selectedOptions = [];
      this.visible = false;
    },
    onCancel() {
      this.visible = false;
      this.searchText = undefined;
      this.searchTextValue = undefined;
      this.selectedOptions = this.appliedFilters;
    },
    filterOptions(options, text) {
      const sortedOptions = Object.entries(options).sort((a, b) => b[1] - a[1]);
      if (text === undefined) {
        return sortedOptions;
      }
      let filtered = sortedOptions.filter(([id]) =>
        id.toLowerCase().match(text.toLowerCase())
      );
      return filtered;
    },
    optionName(option) {
      return option[0];
    },
    optionCounter(option) {
      return option[1];
    },
  },
};
</script>

<style lang="scss" scoped>
.highlight-text {
  display: inline-block;
  // font-weight: 600;
  background: #ffbf00;
  line-height: 16px;
}

.filter {
  &__row {
    display: flex;
    align-items: center;
    &:not(.selected) {
      margin-left: 2em;
    }
    .dropdown {
      margin-right: 0;
      margin-left: auto;
      width: 270px;
      flex-shrink: 0;
    }
  }
  &__label {
    word-break: normal;
    margin: 0 1em 0 0;
    max-width: 166px;
    text-overflow: ellipsis;
    overflow: hidden;
  }
  &__buttons {
    margin-top: 1em;
    text-align: right;
    display: flex;
    & > * {
      width: 100%;
      justify-content: center;
      &:last-child {
        margin-left: $base-space;
      }
    }
  }
  &__remove-button {
    position: relative;
    margin-right: 1em;
    cursor: pointer;
    flex-shrink: 0;
  }
}
</style>
