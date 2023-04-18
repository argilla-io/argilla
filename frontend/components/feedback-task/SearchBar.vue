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
  <form class="searchbar__form" @submit.prevent="searchText(query)">
    <div class="searchbar" :class="{ active: query }" :style="searchBarStyles">
      <svgicon v-if="!query" name="search" width="20" height="20" />
      <BaseButton
        v-else
        class="searchbar__button"
        @click="removeCurrentSearchText()"
      >
        <svgicon name="close" width="20" height="20" />
      </BaseButton>
      <label class="searchbar__label" for="query" v-text="accesibleText" />
      <input
        class="searchbar__input"
        type="text"
        name="query"
        id="query"
        v-model="query"
        :placeholder="placeholder"
      />
    </div>
  </form>
</template>

<script>
import "assets/icons/close";
import "assets/icons/search";

export default {
  props: {
    currentSearchText: {
      type: String,
      default: "",
    },
    placeholder: {
      type: String,
      default: "Introduce your text:",
    },
    accesibleText: {
      type: String,
      default: "Introduce your text",
    },
    bgColor: {
      type: String,
      default: "#ffffff",
    },
  },
  data: () => ({
    text: "",
  }),
  computed: {
    query: {
      get() {
        return this.text || this.currentSearchText;
      },
      set(val) {
        this.text = val;
      },
    },
    searchBarStyles() {
      return { backgroundColor: this.bgColor };
    },
  },
  methods: {
    searchText(query) {
      this.$emit("on-search-text", query);
    },
    removeCurrentSearchText() {
      this.query = "";
      this.$emit("on-search-text", "");
    },
  },
};
</script>

<style lang="scss" scoped>
.searchbar {
  display: flex;
  align-items: center;
  gap: $base-space;
  padding: $base-space * 1.4;
  background: palette(white);
  border-radius: $border-radius-s;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.13);
  transition: all 0.2s ease;
  &:hover {
    box-shadow: 0 6px 10px 0 rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease;
  }
  &__form {
    width: 100%;
  }
  &__button.button {
    padding: 0;
    &:hover {
      .svg-icon {
        fill: $black-87;
      }
    }
    .svg-icon {
      padding: calc($base-space / 2);
    }
  }
  &__label {
    @extend %visuallyhidden;
  }
  &__input {
    width: 100%;
    border: none;
    outline: 0;
    background: none;
  }
  .svg-icon {
    fill: $black-54;
  }
}
</style>
