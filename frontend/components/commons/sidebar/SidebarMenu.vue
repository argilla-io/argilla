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
  <div class="sidebar">
    <span v-for="group in sidebarGroups" :key="group">
      <div class="sidebar__info">
        <p>{{ group }}</p>
        <sidebar-button
          v-for="button in filteredSidebarItems.filter(
            (button) => button.group === group
          )"
          :id="button.id"
          :key="button.id"
          :active-view="[viewMode, currentMetric]"
          :icon="button.icon"
          :tooltip="button.tooltip"
          :type="group"
          @button-action="action(button.action, button.id)"
        />
      </div>
    </span>
    <slot />
  </div>
</template>

<script>
export default {
  props: {
    dataset: {
      type: Object,
      requried: false,
      default: undefined,
    },
    sidebarItems: {
      type: Array,
    },
    currentMetric: {
      type: String,
    },
  },
  computed: {
    filteredSidebarItems() {
      return this.sidebarItems.filter(
        (item) =>
          item.group !== "Metrics" || this.metricsByViewMode.includes(item.id)
      );
    },
    metricsByViewMode() {
      return this.sidebarItems.find(
        (item) => item.id === this.dataset.viewSettings.viewMode
      ).relatedMetrics;
    },
    sidebarGroups() {
      const groups = [
        ...new Set(this.sidebarItems.map((button) => button.group)),
      ];
      return groups;
    },
    viewMode() {
      if (this.isDatasetView) {
        return this.dataset.viewSettings.viewMode;
      }
      return undefined;
    },
    isDatasetView() {
      return this.dataset !== undefined;
    },
  },
  methods: {
    action(action, id) {
      this.$emit(action, id);
    },
  },
};
</script>

<style lang="scss" scoped>
$sidebar-button-size: 45px;
.sidebar {
  top: 0;
  width: $sidebar-button-size;
  min-width: $sidebar-button-size;
  min-height: 100vh;
  min-width: $sidebarMenuWidth;
  background: $bg;
  box-shadow: none;
  pointer-events: all;
  z-index: 1;
  transition: box-shadow 0.2s ease-in-out 0.4s;
  .--metrics & {
    box-shadow: inset 1px 1px 5px -2px #c7c7c7;
    transition: box-shadow 0.2s ease-in-out;
  }
  p {
    text-align: center;
    font-weight: 600;
    @include font-size(12px);
    color: $font-dark;
    margin-bottom: 0.5em;
  }
  a {
    position: relative;
    display: block;
    outline: none;
    z-index: 3;
  }
  &__info {
    position: relative;
    z-index: 1;
    margin-bottom: 2em;
  }
}
a[data-title]:not(.active) {
  @extend %has-tooltip--left;
}
</style>
