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
    :class="{ active: isSearchActive || searchHasFocus }"
    @click="focusInSearch"
  >
    <BaseIconWithBadge
      class="search-area__icon"
      icon="search"
      :show-badge="false"
      iconColor="#acacac"
      badge-vertical-position="top"
      badge-horizontal-position="right"
      badge-border-color="white"
      @click-icon="applySearch"
    />
    <input
      ref="searchRef"
      class="search-area__input"
      type="text"
      v-model.trim="searchValue"
      :placeholder="placeholder"
      :aria-description="description"
      autocomplete="off"
      @focus="searchHasFocus = true"
      @blur="searchHasFocus = false"
      @keydown.enter.exact="applySearch"
      @keydown.arrow-right.stop=""
      @keydown.arrow-left.stop=""
      @keydown.delete.exact.stop=""
      @keydown.enter.exact.stop=""
    />

    <span
      class="search-area__additional-info"
      v-if="localAdditionalInfo"
      v-text="additionalInfo"
    />

    <BaseIconWithBadge
      v-if="showDelete"
      class="search-area__icon --close"
      icon="close"
      :show-badge="false"
      iconColor="#acacac"
      badge-vertical-position="top"
      badge-horizontal-position="right"
      badge-border-color="white"
      @click-icon="resetValue"
    />
  </div>
</template>

<script>
import { isNil } from "lodash";
// TODO - manage only empty strings and not null in the  search component

export default {
  name: "SearchBarComponent",
  props: {
    value: {
      type: String,
      default: "",
    },
    additionalInfo: {
      type: String | null,
      default: null,
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
      searchHasFocus: false,
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
    additionalInfo: {
      inmediate: true,
      handler(newValue) {
        this.localAdditionalInfo = newValue;
      },
    },
  },
  methods: {
    applySearch() {
      this.$emit("input", this.searchValue);
      this.looseFocus();
    },
    looseFocus() {
      this.$refs.searchRef.blur();
    },
    focusInSearch() {
      this.$refs.searchRef.focus();
    },
    resetValue() {
      this.searchValue = "";
      this.localAdditionalInfo = "";
      this.$emit("input", "");
    },
  },
};
</script>

<style lang="scss" scoped>
.search-area {
  display: flex;
  min-width: 300px;
  align-items: center;
  gap: $base-space * 1.5;
  padding: $base-space * 1.2 $base-space * 1.5;
  border: 1px solid palette(grey, 600);
  border-radius: $border-radius-l;
  background: palette(white);
  box-shadow: $shadow-300;
  transition: all 0.2s ease;
  &:hover {
    border: 1px solid rgba(0, 0, 0, 0.1);
    box-shadow: $shadow-500;
    transition: all 0.2s ease;
  }
  &.active {
    border: 1px solid $primary-color;
    box-shadow: none;
  }
  &__icon.button {
    display: flex;
    flex-shrink: 0;
    padding: 0;
    width: 20px;
    height: 20px;
    &.--close {
      width: $base-space * 1.6;
    }
  }
  &__input {
    width: 100%;
    padding: 0;
    border: none;
    outline: 0;
    background: none;
    line-height: 1rem;
    @include input-placeholder {
      color: $black-37;
    }
  }
  &__additional-info {
    @include font-size(13px);
    color: $black-37;
    white-space: nowrap;
  }
}
</style>
