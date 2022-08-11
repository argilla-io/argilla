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
          name="close"
          width="10"
          height="10"
          color="#9b9b9b"
          @click="cleanSearchText"
        ></svgicon>
        <select-options
          v-if="multiLabel"
          ref="options"
          type="multiple"
          v-model="selectedOptions"
          :options="filterSearch(options, searchText)"
        />
        <select-options
          v-else
          ref="options"
          type="single"
          :options="filterSearch(options, searchText)"
          @selected="selectedOption"
        />
        <div
          v-if="multiLabel && filterSearch(options, searchText).length"
          class="selector__buttons"
        >
          <re-button class="primary outline small" @click="onVisibility(false)">
            Cancel
          </re-button>
          <re-button
            class="primary small"
            @click="selectedOption(selectedOptions)"
          >
            Annotate
          </re-button>
        </div>
      </template>
    </FilterDropdown>
  </div>
</template>
<script>
export default {
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
    selectedOption(labels) {
      const labelsFormat = typeof labels === "string" ? [labels] : labels;
      this.$emit("selected", labelsFormat);
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
  &__buttons {
    margin-top: 2em;
    display: flex;
    & > * {
      width: 100%;
      justify-content: center;
      &:last-child {
        margin-left: $base-space;
      }
    }
  }
}
</style>
