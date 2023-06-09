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
    :class="{ active: isSearchActive }"
    @click="focusInSearch"
  >
    <BaseIconWithBadge
      class="searchbar__icon"
      :icon="iconType"
      :show-badge="false"
      iconColor="#acacac"
      badge-vertical-position="top"
      badge-horizontal-position="right"
      badge-border-color="white"
      @click-icon="resetValue"
    />
    <input
      ref="searchRef"
      class="searchbar__input"
      type="text"
      v-model.trim="searchValue"
      :placeholder="placeholder"
      :aria-description="description"
      autocomplete="off"
      @keydown.enter.exact="applySearch"
      @keydown.arrow-right.stop=""
      @keydown.arrow-left.stop=""
      @keydown.delete.exact.stop=""
      @keydown.enter.exact.stop=""
    />
  </div>
</template>

<script>
export default {
  name: "SearchBarComponent",
  props: {
    value: {
      type: String,
      default: () => "",
    },
    placeholder: {
      type: String,
      default: () => "",
    },
    description: {
      type: String,
      default: "Introduce your text",
    },
  },
  data() {
    return {
      searchValue: "",
    };
  },
  computed: {
    isSearchActive() {
      return this.value?.length;
    },
    iconType() {
      return this.searchValue?.length ? "close" : "search";
    },
  },
  watch: {
    value: {
      immediate: true,
      handler(newValue) {
        this.searchValue = newValue ?? "";
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
      if (this.searchValue?.length) {
        this.searchValue = "";
        this.$emit("input", "");
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.search-area {
  display: flex;
  flex: 1;
  align-items: center;
  gap: $base-space;
  width: 300px;
  padding: $base-space * 1.4;
  background: palette(white);
  border-radius: $border-radius-s;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.13);
  transition: all 0.2s ease;
  &:hover {
    box-shadow: 0 6px 10px 0 rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease;
  }
  button {
    display: flex;
    padding: 0;
    &:hover {
      background: $black-4;
    }
  }
  &__icon {
    padding: calc($base-space / 2);
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
</style>
