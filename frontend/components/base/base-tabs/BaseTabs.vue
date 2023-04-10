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
  <ul class="tabs">
    <li class="tab">
      <button
        v-for="{ id, name } in tabs"
        :key="id"
        :class="['tab__button', getTabClass(id)]"
        @click="changeTab(id)"
      >
        <span>{{ name }}</span>
      </button>
    </li>
  </ul>
</template>
<script>
export default {
  props: {
    tabs: {
      type: Array,
      required: true,
    },
    activeTab: {
      type: Object,
      required: true,
    },
  },
  methods: {
    changeTab(id) {
      this.$emit("change-tab", id);
    },
    getTabClass(id) {
      return this.activeTab.id === id || this.tabs.length === 1
        ? "--active"
        : null;
    },
  },
};
</script>
<style lang="scss" scoped>
.tabs {
  display: flex;
  padding: 0;
  list-style: none;
  overflow-y: auto;
  border-bottom: 1px solid $black-10;
  @extend %hide-scrollbar;
  &:before,
  &:after {
    position: absolute;
    content: "";
    height: 40px;
    width: 30px;
    z-index: 1;
  }
  &:before {
    left: 0;
    background: linear-gradient(to right, palette(white), transparent 100%);
  }
  &:after {
    right: 0;
    background: linear-gradient(to left, palette(white), transparent 100%);
  }
}
.tab {
  display: flex;
  &__button {
    padding: $base-space;
    background: none;
    border-top: 0;
    border-right: 0;
    border-left: 0;
    border-bottom: 2px solid transparent;
    transition: border-color 0.3s ease-in-out;
    color: $black-54;
    outline: 0;
    white-space: nowrap;
    cursor: pointer;
    @include font-size(13px);
    &.--active {
      border-color: $primary-color;
      transition: border-color 0.3s ease-in-out;
    }
    &.--active,
    &:hover {
      color: $black-87;
      transition: color 0.2s ease-in-out;
    }
  }
}
</style>
