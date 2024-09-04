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
    <li v-for="{ id, name } in tabs" :key="id" class="tab">
      <button
        :id="id"
        :class="['tab__button', `--${tabSize}`, getTabClass(id)]"
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
    tabSize: {
      type: String,
      default: "small",
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
  position: relative;
  display: flex;
  flex-shrink: 0;
  padding: 0;
  margin-bottom: 0;
  list-style: none;
  overflow-y: auto;
  border-bottom: 1px solid var(--bg-opacity-10);
  @extend %hide-scrollbar;
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
    color: var(--fg-secondary);
    outline: 0;
    white-space: nowrap;
    cursor: pointer;
    &.--small {
      @include font-size(13px);
    }
    &.--large {
      @include font-size(16px);
      padding: $base-space $base-space * 2;
    }
    &.--active {
      border-color: var(--fg-cuaternary);
      transition: border-color 0.3s ease-in-out;
    }
    &.--active,
    &:hover {
      color: var(--fg-primary);
      transition: color 0.2s ease-in-out;
    }
  }
}
</style>
