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
  <div class="filter__row">
    <svgicon
      v-if="appliedFilters.length"
      title="remove field"
      class="filter__remove-button"
      name="cross"
      width="14"
      height="14"
      @click="onRemove()"
    />
    <p class="filter__label" :title="filter.name">{{ filter.name }}:</p>
    <FilterDropdown
      :class="{ highlighted: visible || appliedFilters.length }"
      class="dropdown--filter"
      :visible="visible"
      @visibility="onVisibility"
    >
      <span slot="dropdown-header">
        <span v-if="appliedFilters.length">
          <p v-if="typeof appliedFilters === 'string'">{{ appliedFilters }}</p>
          <p
            v-for="appliedFilter in appliedFilters"
            v-else
            :key="appliedFilter"
          >
            {{ appliedFilter }}
          </p>
        </span>
        <span v-else>
          {{ filter.placeholder }}
        </span>
      </span>
      <div slot="dropdown-content">
        <input
          v-model="searchText"
          class="filter-options"
          type="text"
          autofocus
          :placeholder="placeholder"
        />
        <ul>
          <li
            v-for="(recordsCounter, optionName) in filterOptions(
              filter.options,
              searchText
            )"
            :key="optionName.index"
          >
            <ReCheckbox
              :id="optionName"
              v-model="selectedOptions"
              class="re-checkbox--dark"
              :value="optionName"
            >
              {{ optionName }} ({{ recordsCounter | formatNumber }})
            </ReCheckbox>
          </li>
          <li
            v-if="
              !Object.entries(filterOptions(filter.options, searchText)).length
            "
          >
            0 results
          </li>
        </ul>
        <div class="filter__buttons">
          <ReButton
            class="button-tertiary--small button-tertiary--outline"
            @click="onCancel"
          >
            Cancel
          </ReButton>
          <ReButton class="button-primary--small" @click="onApply">
            Filter
          </ReButton>
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
      if (text === undefined) {
        return options;
      }
      let filtered = Object.fromEntries(
        Object.entries(options).filter(([id]) =>
          id.toLowerCase().match(text.toLowerCase())
        )
      );
      return filtered;
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
      display: block !important;
      width: 100%;
      margin-right: 0.5em;
      min-height: 38px;
      &:last-child {
        margin-right: 0;
      }
    }
  }
  &__remove-button {
    position: absolute;
    left: 20px;
    margin-right: 1em;
    cursor: pointer;
  }
}

.dropdown {
  &__placeholder {
    display: none;
    .dropdown--open & {
      display: block;
    }
  }
  &__selectables {
    vertical-align: middle;
    .dropdown--open & {
      visibility: hidden;
    }
    & + .dropdown__selectables {
      &:before {
        content: ",  ";
        margin-right: 2px;
      }
      &:after {
        content: "...";
        margin-left: -2px;
      }
    }
  }
}
.filter-options {
  &__back {
    color: $primary-color;
    margin-top: 1em;
    display: flex;
    align-items: center;
    &__chev {
      cursor: pointer;
      margin-right: 1em;
      padding: 0.5em;
      &:after {
        content: "";
        border-color: $primary-color;
        border-style: solid;
        border-width: 1px 1px 0 0;
        display: inline-block;
        height: 8px;
        width: 8px;
        transform: rotate(-135deg);
        transition: all 1.5s ease;
        margin-bottom: 2px;
        margin-left: auto;
        margin-right: 0;
      }
    }
  }
  &__button {
    display: flex;
    cursor: pointer;
    min-width: 135px;
    transition: min-width 0.2s ease;
    &.active {
      min-width: 270px;
      transition: min-width 0.2s ease;
    }
    &.hidden {
      opacity: 0;
    }
  }
  &__chev {
    padding-left: 2em;
    margin-right: 0;
    margin-left: auto;
    background: none;
    border: none;
    outline: none;
    &:after {
      content: "";
      border-color: #4a4a4a;
      border-style: solid;
      border-width: 1px 1px 0 0;
      display: inline-block;
      height: 8px;
      width: 8px;
      transform: rotate(43deg);
      transition: all 1.5s ease;
      margin-bottom: 2px;
      margin-left: auto;
      margin-right: 0;
    }
  }
}
</style>
