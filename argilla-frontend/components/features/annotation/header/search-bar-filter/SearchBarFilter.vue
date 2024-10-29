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
      <svgicon name="search" width="16" height="16" aria-hidden="true"/>
    </BaseButton>
    <input
      ref="searchRef"
      class="search-area__input"
      type="text"
      v-model.trim="searchValue"
      role="search"
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
      <svgicon name="close" width="12" height="12" aria-hidden="true" />
    </BaseButton>

    <BaseDropdown
      v-if="fields.length > 1"
      class="search-area__fields"
      :visible="dropdownIsVisible"
      @visibility="onVisibility"
    >
      <template slot="dropdown-header">
        <span class="search-area__fields__header">
          <span class="search-area__fields__header__text">{{
            selectedField.title
          }}</span>
          <svgicon name="chevron-down" height="8" aria-hidden="true"/>
        </span>
      </template>
      <template slot="dropdown-content">
        <ul class="search-area__fields__content">
          <li v-for="field in filteredFields" :key="field.id">
            <BaseButton @on-click="selectField(field)">{{
              field.title
            }}</BaseButton>
          </li>
        </ul>
      </template>
    </BaseDropdown>
  </div>
</template>

<script>
export default {
  name: "SearchBarFilter",
  props: {
    value: {
      type: Object,
      required: true,
    },
    fields: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      searchValue: "",
      isExpanded: false,
      dropdownIsVisible: false,
    };
  },
  computed: {
    isSearchActive() {
      return this.searchValue.length > 0 || this.value.isCompleted;
    },
    showDelete() {
      return this.isSearchActive;
    },
    selectedField() {
      return this.fieldList.find(
        (field) => field.name === this.value.value.field
      );
    },
    fieldList() {
      return [
        {
          id: "all",
          name: "all",
          title: this.$t("all"),
        },
        ...this.fields,
      ];
    },
    filteredFields() {
      return this.fieldList.filter(
        (field) => field.name !== this.value.value.field
      );
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
      if (!this.isSearchActive) return;

      this.value.value = {
        ...this.value.value,
        text: this.searchValue,
        field: this.value.value.field,
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
    onVisibility(value) {
      this.dropdownIsVisible = value;
    },
    selectField(field) {
      this.value.value.field = field.name;
      this.dropdownIsVisible = false;

      this.applySearch();
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
  max-height: $searchBarSize;
  max-width: $searchBarSize;
  border-radius: $border-radius-l;
  transition: all 0.3s ease;
  border: 1px solid transparent;
  &.active,
  &.expanded {
    background: var(--bg-accent-grey-2);
    border: 1px solid var(--bg-opacity-10);
    transition: all 0.3s ease;
    .button.--search {
      color: var(--fg-tertiary);
    }
  }
  &.active,
  &.expanded {
    max-width: 100%;
    .search-area__fields {
      display: block;
    }
  }
  &.expanded:focus-within,
  &.active {
    border: 1px solid var(--fg-cuaternary);
  }
  &__icon.button {
    display: flex;
    flex-shrink: 0;
    padding: $base-space;
    color: var(--fg-secondary);
    &.--search {
      border-radius: $border-radius-l;
      &:hover {
        background: var(--bg-opacity-4);
        color: var(--fg-secondary);
        transition: all 0.3s ease;
      }
    }
  }
  &__input {
    width: 100%;
    padding: 0;
    border: none;
    outline: 0;
    background: none;
    line-height: 1.4;
    color: var(--fg-primary);
    @include input-placeholder {
      color: var(--fg-tertiary);
    }
  }
  &__fields {
    display: none;
    max-width: 30%;
    border-left: 1px solid var(--fg-tertiary);
    flex-shrink: 0;
    &__header {
      display: flex;
      gap: $base-space;
      align-items: center;
      padding-inline: $base-space;
      min-width: 0;
      line-height: 1em;
      &__text {
        font-weight: 500;
        @include truncate;
      }
      &:hover {
        cursor: pointer;
        color: var(--fg-primary);
      }
      .svg-icon {
        flex-shrink: 0;
      }
    }
    &__content {
      list-style: none;
      padding: $base-space;
      margin: 0;
      li {
        padding: $base-space;
        border-radius: $border-radius-s;
        transition: background-color 0.3s ease;
        &:hover {
          background: var(--bg-opacity-4);
          cursor: pointer;
          transition: background-color 0.3s ease;
        }
      }
      .button {
        display: block;
        max-width: 200px;
        text-align: left;
        padding: 0;
        font-weight: normal;
        line-height: 1.2em;
        @include truncate;
      }
    }
    :deep(.dropdown__content) {
      min-width: 100%;
      left: auto;
      right: 0;
      top: calc(100% + $base-space * 2);
    }
    :deep(.dropdown__header) {
      &:hover,
      &:focus {
        background: none;
      }
    }
  }
}
.button[data-title] {
  overflow: visible;
  @include tooltip-mini("top", 8px);
}
</style>
