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
      class="searchbar__icon"
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
      class="searchbar__input"
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
      class="additional-info"
      v-if="isSearchActive"
      v-text="additionalInfo"
    />

    <BaseIconWithBadge
      v-if="showDelete"
      class="searchbar__icon"
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
      searchHasFocus: false,
    };
  },
  computed: {
    isSearchActive() {
      return this.value?.length ?? false;
    },
    isActiveSearchEmpty() {
      return isNil(this.value) || this.value.length === 0;
    },
    showDelete() {
      if (isNil(this.searchValue)) return false;
      if (this.isActiveSearchEmpty && this.searchValue.length === 0)
        return false;

      return true;
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
      this.$emit("input", "");
    },
  },
};
</script>

<style lang="scss" scoped>
.search-area {
  display: flex;
  width: 300px;
  align-items: center;
  gap: $base-space;
  padding: $base-space * 1.4;
  filter: drop-shadow(0px 1px 2px rgba(185, 185, 185, 0.5));
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 25px;
  background: palette(white);
  transition: all 0.2s ease;
  &:hover {
    border: 1px solid rgba(0, 0, 0, 0.1);
    box-shadow: 0px 8px 20px rgba(93, 105, 151, 0.3);
    transition: all 0.2s ease;
  }
  button {
    display: flex;
    padding: 0;
    &:hover {
      background: $black-4;
    }
  }
  input {
    width: 100%;
    height: 1rem;
    padding: 0;
    border: none;
    outline: 0;
    background: none;
    line-height: 1rem;
  }
}

.searchbar__icon {
  width: 36px;
}

.additional-info {
  font-size: 14px;
  font-size: 0.875rem;
  color: rgba(0, 0, 0, 0.37);
  text-wrap: nowrap;
}

.active {
  border: 1px solid #3e5cc9;
}
</style>
