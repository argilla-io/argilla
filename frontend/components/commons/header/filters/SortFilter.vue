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
  <div class="sort">
    <svgicon
      v-if="selectedField"
      title="remove field"
      class="sort__remove-button"
      name="cross"
      width="14"
      height="14"
      @click="removeField()"
    />
    <FilterDropdown
      class="dropdown--filter"
      :class="{ highlighted: visible }"
      :visible="visible"
      @visibility="onVisibility"
    >
      <span slot="dropdown-header">
        <span v-if="selectedField">{{ selectedField.name }}</span>
        <span v-else>Sort by</span>
      </span>
      <div slot="dropdown-content">
        <input
          v-model="searchText"
          class="filter-options"
          type="text"
          autofocus
          placeholder="Search..."
        />
        <ul>
          <li v-for="option in filteredSortOptions" :key="option.text">
            <a href="#" @click.prevent="addField(option)">
              {{ option.name }}
            </a>
          </li>
        </ul>
      </div>
    </FilterDropdown>
    <p
      v-if="selectedField"
      title="sort direction"
      class="sort__direction"
      @click="selectSortDirection()"
    >
      <svgicon width="17" height="24" :name="defaultSortedByDir === 'asc' ? 'arrow-top' : 'arrow-bottom'" />
    </p>
  </div>
</template>

<script>
import "assets/icons/cross";
import "assets/icons/arrow-top";
import "assets/icons/arrow-bottom";
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
    searchText: undefined,
  }),
  computed: {
    filteredSortOptions() {
      if (this.searchText === undefined) {
        return this.formatSortOptions;
      }
      let filtered = this.formatSortOptions.filter((opt) =>
        opt.name.toLowerCase().match(this.searchText.toLowerCase())
      );
      return filtered;
    },
    formatSortOptions() {
      return this.sortOptions.map((opt) => {
        if (opt.group.toLowerCase() === "metadata") {
          return {
            ...opt,
            name: `Metadata.${opt.name}`,
          };
        }
        return opt;
      });
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
  },
};
</script>

<style lang="scss" scoped>
.sort {
  display: flex;
  align-items: center;
  &__remove-button {
    position: absolute;
    left: 20px;
    margin-right: 1em;
    cursor: pointer;
  }
  &__direction {
    position: relative;
    padding: 0.5em;
    @include font-size(20px);
    margin: 0 0 0 0.5em;
    background: palette(grey, light);
    border-radius: 5px;
    min-width: 50px;
    min-height: 45px;
    text-align: center;
    cursor: pointer;
  }
  .dropdown {
    width: 100%;
    max-width: 280px;
    a {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      text-decoration: none;
      max-width: 250px;
      display: block;
    }
  }
}
</style>
