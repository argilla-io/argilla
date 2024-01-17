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
  <div
    class="search-area"
    :class="{ active: isSearchActive, expanded: isExpanded }"
  >
    <BaseButton
      @on-click="applySearch"
      class="search-area__icon --search"
      :data-title="$t('search')"
    >
      <svgicon name="search" width="16" height="16" />
    </BaseButton>
    <input
      ref="searchRef"
      class="search-area__input"
      type="text"
      v-model.trim="searchValue"
      :placeholder="placeholder"
      :aria-description="description"
      autocomplete="off"
      @keydown.enter.exact.stop="applySearch"
      @keydown.arrow-right.stop=""
      @keydown.arrow-left.stop=""
      @keydown.delete.exact.stop=""
      @keydown.backspace.exact.stop=""
    />
    <BaseButton
      @on-click="resetValue"
      v-if="showDelete"
      class="search-area__icon --close"
    >
      <svgicon name="close" width="12" height="12" />
    </BaseButton>
  </div>
</template>

<script>
import { isNil } from "lodash";

export default {
  name: "SearchBarComponent",
  props: {
    value: {
      type: String,
      default: "",
    },
    placeholder: {
      type: String,
      default: "",
    },
    description: {
      type: String,
      default: "Introduce a text",
    },
  },
  data() {
    return {
      searchValue: "",
      localAdditionalInfo: "",
      isExpanded: false,
    };
  },
  computed: {
    isSearchActive() {
      return !(isNil(this.value) || this.value.length === 0);
    },
    isSearchValueEmpty() {
      return isNil(this.searchValue) || this.searchValue.length === 0;
    },
    showDelete() {
      return !this.isSearchValueEmpty || this.isSearchActive;
    },
  },
  watch: {
    value: {
      immediate: true,
      handler(newValue) {
        this.searchValue = newValue;
      },
    },
  },
  methods: {
    applySearch() {
      this.$emit("input", this.searchValue);
      if (this.isSearchValueEmpty) {
        this.isExpanded = !this.isExpanded;
        this.$refs.searchRef.focus();
      } else {
        this.collapseSearch();
        this.$refs.searchRef.blur();
      }
    },
    resetValue() {
      this.searchValue = "";
      this.$emit("input", "");
      this.collapseSearch();
    },
    collapseSearch() {
      this.isExpanded = false;
    },
  },
};
</script>

<style lang="scss" scoped>
$searchBarSize: $base-space * 4;
.search-area {
  display: flex;
  align-items: center;
  gap: $base-space;
  padding: 7px;
  max-height: $searchBarSize;
  max-width: $searchBarSize;
  border-radius: $border-radius-l;
  transition: all 0.3s ease;
  border: 1px solid transparent;
  &:hover {
    background: $black-4;
    transition: all 0.3s ease;
  }
  &.active,
  &.expanded {
    background: palette(white);
    border: 1px solid $black-10;
    transition: all 0.3s ease;
    .button.--search {
      color: $black-37;
    }
  }
  &.active,
  &.expanded {
    max-width: 100%;
  }
  &.expanded:focus-within,
  &.active {
    border: 1px solid $primary-color;
  }
  &__icon.button {
    display: flex;
    flex-shrink: 0;
    padding: 0;
    color: $black-54;
  }
  &__input {
    width: 100%;
    padding: 0;
    border: none;
    outline: 0;
    background: none;
    line-height: 1.4;
    @include input-placeholder {
      color: $black-37;
    }
  }
}
.button[data-title] {
  overflow: visible;
  @include tooltip-mini("top", 16px);
}
</style>
