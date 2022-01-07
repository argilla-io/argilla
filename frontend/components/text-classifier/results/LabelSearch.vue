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
  <ReInputContainer class="searchbar">
    <svgicon v-if="!filter" name="search" width="20" height="40" />
    <svgicon
      v-else
      class="searchbar__button"
      name="cross"
      width="20"
      height="14"
      @click="filter = ''"
    />
    <ReInput v-model="filter" placeholder="Search labels" />
  </ReInputContainer>
</template>
<script>
import "assets/icons/search";
import "assets/icons/cross";

export default {
  props: {
    searchText: {
      type: String,
      default: "",
    },
  },
  computed: {
    filter: {
      get() {
        return this.searchText;
      },
      set(val) {
        this.$emit("input", val);
      },
    },
  },
};
</script>
<style lang="scss" scoped>
.searchbar {
  width: 285px;
  min-height: 43px;
  border: none;
  display: flex;
  align-items: center;
  transition: all 0.2s ease;
  margin: 1.5em auto 0.5em 0;
  pointer-events: all;
  font-weight: 600;
  @include font-size(14px);
  input {
    color: $font-secondary-dark;
    font-weight: 600;
    @include input-placeholder {
      color: $font-secondary-dark;
    }
  }
  .svg-icon {
    fill: $font-secondary-dark;
    margin: auto 1em auto auto;
  }
  &__button {
    cursor: pointer;
  }
}
</style>
