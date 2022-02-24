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
    <span v-for="group in sidebarButtonGroups" :key="group.name">
      <div class="sidebar__info">
        <p>{{ group.name }}</p>
        <sidebar-button
          v-for="button in group.elements"
          :id="button.id"
          :key="button.id"
          :active-view="group.isActive"
          :icon="button.icon"
          :tooltip="button.tooltip"
          :type="group.name"
          @button-action="group.action"
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
  },
  data: () => {
    return {
      currentViewMode: "explore",
      width: window.innerWidth,
      visibleSidebarInfo: undefined,
    };
  },
  computed: {
    sidebarButtonGroups() {
      // TODO: sidebar must be customized for task view
      var groups = [];
      if (this.isDatasetView) {
        const modeGroup = {
          name: "Mode",
          action: this.onChangeViewMode,
          isActive: this.currentViewMode,
          elements: [
            {
              id: "explore",
              tooltip: "Explore",
              icon: "explore-view",
            },
            {
              id: "annotate",
              tooltip: "Annotate",
              icon: "annotate-view",
            },
          ],
        };

        if (this.showLabellingRules) {
          modeGroup.elements.push({
            id: "labelling-rules",
            tooltip: "Define rules",
            icon: "labelling-rules-view",
          });
        }
        groups.push(modeGroup);

        const metrics = {
          name: "Metrics",
          condition: this.isDatasetView,
          action: this.onShowMetric,
          isActive: this.visibleSidebarInfo,
          elements: [
            {
              id: "progress",
              tooltip: "Progress",
              icon: "progress",
            },
            {
              id: "stats",
              tooltip: "Stats",
              icon: "metrics",
            },
          ],
        };
        groups.push(metrics);
      }
      const refresh = {
        name: "Refresh",
        action: this.onRefresh,
        elements: [
          {
            id: "refresh",
            tooltip: "Refresh",
            icon: "refresh",
          },
        ],
      };
      groups.push(refresh);
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
    showLabellingRules() {
      return (
        this.isDatasetView &&
        !this.dataset.isMultiLabel &&
        this.dataset.task === "TextClassification"
      );
    },
  },
  watch: {
    viewMode(newValue) {
      this.currentViewMode = newValue;
    },
  },
  updated() {
    window.onresize = () => {
      this.width = window.innerWidth;
    };
  },
  mounted() {
    this.currentViewMode = this.viewMode;
  },
  methods: {
    onShowMetric(info) {
      this.$emit("showMetric", info);
      if (this.visibleSidebarInfo !== info) {
        this.visibleSidebarInfo = info;
      } else {
        this.visibleSidebarInfo = undefined;
      }
    },
    onChangeViewMode(id) {
      this.$emit("changeViewMode", id);
    },
    onRefresh() {
      this.$emit("refresh");
    },
  },
};
</script>

<style lang="scss" scoped>
$sidebar-button-size: 45px;
$color: #333346;
.sidebar {
  position: fixed;
  top: 56px;
  right: 0;
  background: $bg;
  width: $sidebar-button-size;
  min-width: $sidebar-button-size;
  min-height: 100vh;
  min-width: 90px;
  border-left: 1px solid palette(grey, smooth);
  z-index: 2;
  p {
    text-align: center;
    font-weight: 600;
    @include font-size(12px);
    color: $color;
  }
  a {
    position: relative;
    display: block;
    outline: none;
  }
  &__info {
    position: relative;
    z-index: 1;
    margin-bottom: 5em;
  }
}
a[data-title]:not(.active) {
  @extend %hastooltip;
  &:after {
    padding: 0.5em 1em;
    top: 0;
    right: calc(100% + 10px);
    transform: none;
    background: $color;
    color: white;
    border: none;
    border-radius: 3px;
    @include font-size(14px);
    font-weight: 600;
  }
  &:before {
    right: calc(100% + 3px);
    top: 0.65em;
    border-top: 7px solid transparent;
    border-bottom: 7px solid transparent;
    border-left: 7px solid $color;
  }
}
</style>
