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
  <BaseInputContainer
    class="search-area"
    :class="[filter ? 'active' : null, isCollapsed ? '--collapsed' : null]"
    ><BaseButton
      class="search-area__button__search"
      @click="toggleSearchBar"
      aria-label="search"
    >
      <svgicon
        name="search"
        width="20"
        height="20"
        color="var(--fg-secondary)"
        aria-hidden="true"
      />
    </BaseButton>
    <BaseInput
      v-show="!isCollapsed"
      :autofocus="!isCollapsed"
      class="search-area__input"
      role="search"
      v-model="filter"
      :placeholder="placeholder"
    />
    <BaseButton
      v-show="!isCollapsed"
      class="search-area__button__close"
      @click="removeFilter"
      aria-label="close"
    >
      <svgicon
        v-if="filter || !isCollapsed"
        class="search-area__icon --close"
        name="close"
        color="var(--fg-secondary)"
        width="14"
        height="14"
        aria-hidden="true"
      />
    </BaseButton>
  </BaseInputContainer>
</template>
<script>
import "assets/icons/search";
import "assets/icons/close";

export default {
  props: {
    querySearch: {
      type: String,
      default: "",
    },
    placeholder: {
      type: String,
      default: "Search",
    },
    collapsed: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      filter: this.value,
      isCollapsed: this.collapsed,
    };
  },
  watch: {
    querySearch(val) {
      this.filter = val;
    },
    filter(val) {
      this.$emit("input", val);
    },
  },
  methods: {
    toggleSearchBar() {
      this.isCollapsed = !this.isCollapsed;
    },
    removeFilter() {
      this.filter = "";
      this.isCollapsed = true;
    },
  },
};
</script>
<style lang="scss" scoped>
$searchBarSize: $base-space * 4;
.search-area {
  display: flex;
  min-width: 300px;
  max-height: $searchBarSize;
  max-width: $searchBarSize;
  align-items: center;
  gap: $base-space * 1.5;
  padding: $base-space * 1.2 $base-space * 1.5;
  border: 1px solid var(--bg-opacity-10);
  border-radius: $border-radius-xl;
  background: var(--bg-accent-grey-1);
  transition: all 0.2s ease;
  &.--collapsed {
    max-width: 34px;
    min-width: 0;
    padding: 0;
    overflow: hidden;
    border: none;
    .button {
      height: 34px;
      width: 34px;
      border-radius: 50%;
      justify-content: center;
    }
    &:hover {
      .button {
        background: var(--bg-opacity-4);
      }
    }
  }

  &.active,
  &.re-input-focused {
    border: 1px solid var(--fg-cuaternary);
  }
  &__button {
    &__search {
      padding: 0;
      min-width: 20px;
    }
    &__close {
      padding: 0;
    }
  }
  &__icon {
    display: flex;
    flex-shrink: 0;
    padding: 0;
    &.--close {
      width: $base-space * 1.6;
      cursor: pointer;
    }
  }
  &__input.input {
    width: 100%;
    height: auto;
    padding: 0;
    border: none;
    outline: 0;
    background: none;
    line-height: 1rem;
    color: var(--fg-secondary);
    @include input-placeholder {
      color: var(--fg-tertiary);
    }
  }
}
</style>
