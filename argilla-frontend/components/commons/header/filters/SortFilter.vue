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
  <div :class="[selectedField ? 'selected' : '', 'sort']">
    <base-button
      v-if="selectedField"
      class="filter__remove-button"
      @click="removeField()"
    >
      <svgicon title="remove field" name="close" width="14" height="14" />
    </base-button>
    <FilterDropdown
      color-type="grey"
      :class="{ highlighted: visible }"
      :visible="visible"
      @visibility="onVisibility"
    >
      <span slot="dropdown-header">
        <span v-if="selectedField">{{ selectedField.name }}</span>
        <span v-else>Sort by</span>
      </span>
      <div slot="dropdown-content">
        <select-options-search v-model="searchText" />
        <select-options
          ref="options"
          type="single"
          :option-name="optionName"
          :options="filteredSortOptions"
          @selected="addField"
        />
      </div>
    </FilterDropdown>
    <base-button
      v-if="selectedField"
      title="sort direction"
      class="sort__direction secondary light"
      @click="selectSortDirection()"
    >
      <svgicon
        width="24"
        height="24"
        :name="defaultSortedByDir === 'asc' ? 'arrow-up' : 'arrow-down'"
      />
    </base-button>
  </div>
</template>

<script>
import "assets/icons/close";
import "assets/icons/arrow-up";
import "assets/icons/arrow-down";
export default {
  props: {
    sortOptions: {
      type: Array,
      required: true,
    },
    selectedField: {
      type: Object,
      default: undefined,
    },
  },
  data: () => ({
    visible: false,
    defaultSortedBy: undefined,
    defaultSortedByDir: "asc",
    searchText: "",
  }),
  computed: {
    filteredSortOptions() {
      return this.sortOptions.filter((opt) =>
        opt.name.toLowerCase().match(this.searchText.toLowerCase())
      );
    },
  },
  mounted() {
    this.getSortDirection();
  },
  updated() {
    this.getSortDirection();
  },
  methods: {
    onVisibility(value) {
      this.visible = value;
    },
    getSortDirection() {
      if (this.selectedField) {
        this.defaultSortedByDir = this.selectedField.order;
      }
    },
    selectSortDirection() {
      this.defaultSortedByDir === "asc"
        ? (this.defaultSortedByDir = "desc")
        : (this.defaultSortedByDir = "asc");
      this.$emit("addSortField", this.selectedField, this.defaultSortedByDir);
    },
    removeField() {
      this.$emit("removeSortField");
    },
    addField(currentSort) {
      this.visible = false;
      this.defaultSortedBy = currentSort;
      this.$emit("addSortField", currentSort, this.defaultSortedByDir);
    },
    optionName(option) {
      return option.name;
    },
  },
};
</script>

<style lang="scss" scoped>
.sort {
  display: flex;
  align-items: center;
  &__direction {
    position: relative;
    padding: 0.5em;
    @include font-size(20px);
    margin: 0 0 0 0.5em;
    background: palette(grey, 700);
    border-radius: $border-radius;
    min-width: 50px;
    min-height: 45px;
    text-align: center;
    cursor: pointer;
    display: flex;
    .svg-icon {
      margin: auto;
    }
  }
  &:not(.selected) {
    margin-left: 2em;
  }
  .dropdown {
    width: 100%;
    max-width: 270px;
  }
}
</style>
