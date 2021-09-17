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
  <div class="selector">
    <p
      v-if="filteredOptions.length"
      class="selector__header"
      @click="openSelector"
    >
      {{ selectedOption.name }}
    </p>
    <p v-else>{{ selectedOption.name }}</p>
    <transition name="fade">
      <ul
        v-if="showOptionsSelector"
        v-click-outside="onClickOutside"
        class="selector__body"
      >
        <li v-for="option in filteredOptions" :key="option.id">
          <a href="#" @click.prevent="selectOption(option)">{{
            option.name
          }}</a>
        </li>
      </ul>
    </transition>
  </div>
</template>

<script>
export default {
  props: {
    selectedOption: {
      type: Object,
      required: true,
    },
    options: {
      type: Array,
      required: true,
    },
  },
  data: () => {
    return {
      showOptionsSelector: false,
    };
  },
  computed: {
    filteredOptions() {
      return this.options.filter((o) => o.name !== this.selectedOption.name);
    },
  },
  methods: {
    openSelector() {
      this.showOptionsSelector = !this.showOptionsSelector;
    },
    selectOption(option) {
      this.$emit("selectOption", option);
      this.showOptionsSelector = false;
    },
    onClickOutside() {
      this.showOptionsSelector = false;
    },
  },
};
</script>
<style lang="scss" scoped>
.selector {
  position: relative;
  margin-bottom: 2em;
  &__header {
    cursor: pointer;
    border: 1px solid palette(grey, smooth);
    border-radius: 5px;
    padding: 0.5em 1em;
    color: $font-secondary-dark;
    @include font-size(13px);
    display: flex;
    align-items: center;
    &:after {
      content: "";
      border-color: palette(grey, dark);
      border-style: solid;
      border-width: 1px 1px 0 0;
      display: inline-block;
      height: 8px;
      width: 8px;
      transform: rotate(133deg);
      transition: all 1.5s ease;
      margin-bottom: 2px;
      margin-left: auto;
    }
  }
  &__body {
    display: block;
    padding: 1em;
    background: white;
    border: 1px solid palette(grey, smooth);
    list-style: none;
    position: absolute;
    top: 100%;
    z-index: 1;
    width: 100%;
    margin-top: 0;
    a {
      padding: 0.5em 0;
      display: block;
      text-decoration: none;
      outline: none;
      &:hover {
        font-weight: 600;
      }
    }
  }
}
</style>
