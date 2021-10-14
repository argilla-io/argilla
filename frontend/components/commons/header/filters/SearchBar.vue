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
  <form @submit.prevent="submit(query)">
    <div
      :class="['searchbar__container', { active: query }]"
    >
      <ReInputContainer class="searchbar">
        <svgicon v-if="!query" name="search" width="20" height="40" />
        <svgicon
          v-else
          class="searchbar__button"
          name="cross"
          width="20"
          height="14"
          @click="removeFilter()"
        />
        <ReInput
          ref="input"
          v-model="query"
          class="searchbar__input"
          placeholder="Search records"
        />
      </ReInputContainer>
    </div>
  </form>
</template>

<script>
import "assets/icons/cross";
import "assets/icons/search";

export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data: () => ({
    queryText: null,
  }),
  computed: {
    query: {
      get() {
        return this.queryText === null
          ? this.dataset.query.text
          : this.queryText;
      },
      set(val) {
        this.queryText = val;
      },
    },
  },
  methods: {
    submit(query) {
      this.$refs.input.$el.blur();
      this.$emit("submit", query);
    },
    removeFilter() {
      this.query = ''
      this.$emit("submit", this.query);
    }
  },
};
</script>

<style lang="scss" scoped>
.searchbar {
  background: $lighter-color;
  width: 285px;
  min-height: 43px;
  border: none;
  padding: 0 1em;
  display: flex;
  align-items: center;
  transition: all 0.2s ease;
  margin-right: 0;
  margin-left: auto;
  pointer-events: all;
  border-radius: 5px;
  &__container {
    position: relative;
    max-width: 280px;
    margin-right: auto;
    margin-left: 0;
  }
  // &.re-input-focused {
  //   border: 2px solid $secondary-color;
  //   .svg-icon {
  //     fill: $secondary-color;
  //   }
  // }
  .svg-icon {
    fill: $primary-color;
    margin: auto 1em auto 1em;
  }
  &:hover {
    box-shadow: 0px 3px 8px 3px rgba(222, 222, 222, 0.4)
  }
  &__button {
    cursor: pointer;
  }
}
</style>
