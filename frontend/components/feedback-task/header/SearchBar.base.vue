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
      @on-click="openOrApply"
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
      :placeholder="$t('searchPlaceholder')"
      :aria-description="$t('searchPlaceholder')"
      autocomplete="off"
      @keydown.stop=""
      @keypress.enter.stop="applySearch"
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
export default {
  name: "SearchBarComponent",
  props: {
    value: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      searchValue: "",
      isExpanded: false,
    };
  },
  computed: {
    isSearchActive() {
      return this.searchValue.length > 0 || this.value.isCompleted;
    },
    showDelete() {
      return this.isSearchActive;
    },
  },
  watch: {
    value: {
      immediate: true,
      deep: true,
      handler(newValue) {
        this.searchValue = newValue.value.text;
      },
    },
  },
  methods: {
    openOrApply() {
      if (this.isExpanded && this.isSearchActive) {
        this.applySearch();
      } else {
        this.isExpanded = !this.isExpanded;

        if (this.isExpanded) {
          this.$refs.searchRef.focus();
        } else {
          this.$refs.searchRef.blur();
        }
      }
    },
    applySearch() {
      this.value.value = {
        ...this.value.value,
        text: this.searchValue,
      };

      this.$refs.searchRef.blur();
    },
    resetValue() {
      this.collapseSearch();

      this.value.reset();
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
