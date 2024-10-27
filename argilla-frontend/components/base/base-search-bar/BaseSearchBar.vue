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
  <base-input-container class="search-area" :class="filter ? 'active' : null">
    <svgicon name="search" width="20" height="20" color="#acacac" aria-hidden="true" />
    <base-input
      class="search-area__input"
      role="search"
      v-model="filter"
      :placeholder="placeholder"
    />
    <svgicon
      v-if="filter"
      class="search-area__icon --close"
      name="close"
      color="#acacac"
      width="14"
      height="14"
      @click="filter = undefined"
      aria-hidden="true"
    />
  </base-input-container>
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
  },
  data() {
    return {
      filter: this.value,
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
  border-radius: $border-radius-l;
  background: var(--bg-accent-grey-1);
  transition: all 0.2s ease;

  &.active,
  &.re-input-focused {
    border: 1px solid var(--fg-cuaternary);
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
