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
    <filter-dropdown
      tooltip="Annotate"
      :visible="visible"
      @visibility="onVisibility"
    >
      <template #dropdown-header>
        <span data-title="Annotate">
          <svgicon name="pen"></svgicon>
        </span>
      </template>
      <template #dropdown-content>
        <select-options-search
          allow-clear
          @clear="clearSearchText"
          v-model="searchText"
          placeholder="Search label..."
        />
        <div class="wrapper">
          <div class="labels">
            <base-button
              v-for="option in filterSearch(options)"
              :key="option"
              class="clear label-text"
              @click.prevent="selectedOption(option)"
            >
              {{ option }}
            </base-button>
            <p v-if="!filterSearch(options).length">0 results</p>
          </div>
        </div>
      </template>
    </filter-dropdown>
  </div>
</template>
<script>
import "assets/icons/pen";
export default {
  props: {
    record: Object,
    options: Array,
  },
  data: () => ({
    visible: false,
    searchText: null,
  }),
  methods: {
    onVisibility(value) {
      this.visible = value;
      this.searchText = undefined;
    },
    selectedOption(label) {
      this.$emit("selected", [label]);
      this.visible = false;
    },

    clearSearchText() {
      this.searchText = null;
    },
    filterSearch(options) {
      if (!this.searchText) {
        return options;
      }
      return options.filter((item) =>
        item.toLowerCase().match(this.searchText.toLowerCase())
      );
    },
  },
};
</script>
<style lang="scss" scoped>
.wrapper {
  max-height: 200px;
  overflow: auto;
  @extend %hide-scrollbar;
}
.labels {
  display: flex;
  flex-flow: column;
  gap: $base-space;
}
.label-text {
  cursor: pointer;
  background: #f0f0fe;
  border-radius: 8px;
  color: #4c4ea3;
  padding: calc($base-space / 2) $base-space;
  @include truncate;
  width: auto;
  margin-right: auto;
  @include font-size(13px);
  font-weight: 500;
  &:hover {
    background: darken(#f0f0fe, 2%);
  }
  &:active {
    background: #4c4ea3;
    color: palette(white);
  }
}
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
