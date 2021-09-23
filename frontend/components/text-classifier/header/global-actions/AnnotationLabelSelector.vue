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
  <div>
    <FilterDropdown
      class="selector"
      :visible="visible"
      @visibility="onVisibility"
    >
      <template #dropdown-header>
        <span class="dropdown__text">Annotate as...</span>
      </template>
      <template #dropdown-content>
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
          @click="cleanSearchText"
        ></svgicon>
        <ul v-if="multiLabel" class="selector__list">
          <li
            v-for="option in filterSearch(options, searchText)"
            :key="option"
            :title="option"
            class="selector__option"
          >
            <ReCheckbox
              :id="option"
              v-model="selectedOptions"
              class="re-checkbox--dark"
              :value="option"
            >
              {{ option }}
            </ReCheckbox>
          </li>
        </ul>
        <ul v-else class="selector__list">
          <li
            v-for="option in filterSearch(options, searchText)"
            :key="option.index"
            class="selector__option"
            @click="selected([option])"
          >
            <span :data-title="option">
              {{ option | truncate(30) }}
            </span>
          </li>
        </ul>
        <div
          v-if="multiLabel && filterSearch(options, searchText).length"
          class="selector__buttons"
        >
          <ReButton
            class="button-tertiary--small button-tertiary--outline"
            @click="onVisibility(false)"
          >
            Cancel
          </ReButton>
          <ReButton
            class="button-primary--small"
            @click="selected(selectedOptions)"
          >
            Apply
          </ReButton>
        </div>
      </template>
    </FilterDropdown>
  </div>
</template>
<script>
import "assets/icons/ignore";

export default {
  filters: {
    truncate(string, value) {
      if (string.length > value) {
        return `${string.substring(0, value)}...`;
      }
      return string;
    },
  },
  props: {
    record: Object,
    options: Array,
    multiLabel: Boolean,
  },
  data: () => ({
    visible: false,
    searchText: undefined,
    showTooltipOnHover: false,
    selectedOptions: [],
  }),
  methods: {
    onVisibility(value) {
      this.visible = value;
      this.searchText = undefined;
    },
    selected(labels) {
      this.$emit("selected", labels);
      this.visible = false;
      this.selectedOptions = [];
    },

    cleanSearchText() {
      this.searchText = undefined;
    },
    filterSearch(options, text) {
      if (text === undefined) {
        return options;
      }
      return options.filter((item) =>
        item.toLowerCase().match(text.toLowerCase())
      );
    },
    showTooltip(data, e) {
      const { tooltip } = this.$refs;
      const el = e.currentTarget;
      if (e.currentTarget && data.length >= 30) {
        tooltip.innerHTML = data;
        this.showTooltipOnHover = true;
        const offset =
          el.getBoundingClientRect().top -
          el.offsetParent.getBoundingClientRect().top;
        tooltip.style.top = `${offset - 35}px`;
      } else {
        this.showTooltipOnHover = false;
      }
    },
  },
};
</script>
<style lang="scss" scoped>
.selector {
  &__option {
    display: block;
    padding: 0.5em 0;
    text-align: left;
    font-weight: 400;
    .re-checkbox {
      margin: 0;
      display: flex;
      ::v-deep label {
        max-width: 140px;
        display: block;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
      }
    }
    cursor: pointer;
    &:hover {
      color: $secondary-color;
    }
  }
  &__buttons {
    margin-top: 1em;
    text-align: right;
    display: flex;
    & > * {
      margin-right: 0.5em;
    }
  }
  ::v-deep .dropdown__content {
    transform: translate 0;
  }
}
</style>
