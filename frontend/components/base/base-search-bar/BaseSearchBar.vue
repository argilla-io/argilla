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
    <svgicon name="search" width="20" height="20" color="#acacac" />
    <base-input
      class="search-area__input"
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
    />
  </base-input-container>
</template>
<script>
import "assets/icons/search";
import "assets/icons/close";

export default {
  props: {
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
    filter(val) {
      this.$emit("input", val);
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
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: $border-radius-l;
  background: palette(white);
  box-shadow: $shadow-300;
  transition: all 0.2s ease;
  &:hover {
    border: 1px solid rgba(0, 0, 0, 0.1);
    box-shadow: $shadow-500;
    transition: all 0.2s ease;
  }
  &.active,
  &.re-input-focused {
    border: 1px solid $primary-color;
    box-shadow: $shadow-300;
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
    @include input-placeholder {
      color: $black-37;
    }
  }
}
</style>
