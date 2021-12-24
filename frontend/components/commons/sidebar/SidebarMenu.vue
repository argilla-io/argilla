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
    <template v-if="isDatasetView">
      <div class="sidebar__info">
        <p>Mode</p>
        <sidebar-button v-if="button.condition !== false" :active-view="currentViewMode" :icon="button.icon" :tooltip="button.tooltip" :id="button.id" v-for="button in sidebarInfoOptions.filter(b => b.type === 'view-mode')" :key="button.id" @change-view-mode="onChangeViewMode" />
      </div>
      <div class="sidebar__info">
        <p>Metrics</p>
        <a
          v-for="sidebarInfo in sidebarInfoOptions"
          :key="sidebarInfo.id"
          :class="['sidebar__info__button', visibleSidebarInfo === sidebarInfo.id ? 'active' : null]"
          href="#"
          :data-title="sidebarInfo.tooltip"
          @click.prevent="showSidebarInfo(sidebarInfo.id)"
        >
          <svgicon v-if="visibleSidebarInfo === sidebarInfo.id"
            class="sidebar__info__icon-help"
            name="double-chev"
          ></svgicon>
          <svgicon :name="sidebarInfo.icon"></svgicon>
        </a>
      </div>
    </template>
    <div class="sidebar__info">
      <p>Refresh</p>
      <a href="#" @click.prevent="$emit('refresh')">
        <svgicon name="refresh"></svgicon>
      </a>
    </div>
    <slot />
  </div>
</template>

<script>
import "assets/icons/refresh";
import "assets/icons/explore-view";
import "assets/icons/annotate-view";
import "assets/icons/labelling-rules-view";
import "assets/icons/progress";
import "assets/icons/metrics";
import "assets/icons/double-chev";
import "assets/icons/check3";
export default {
  props: {
    dataset: {
      type: Object,
      requried: false,
      default: undefined
    },
  },
  data: () => {
    return {
      currentViewMode: 'explore',
      width: window.innerWidth,
      visibleSidebarInfo: undefined,
    };
  },
  computed: {
    sidebarInfoOptions() {
      return [
        { 
          type: 'view-mode',
          id: "explore",
          tooltip: "Explore",
          icon: "explore-view"
        },
        { 
          type: 'view-mode',
          id: "annotate",
          tooltip: "Annotate",
          icon: "annotate-view"
        },
        { 
          type: 'view-mode',
          id: "labelling-rules",
          tooltip: "Define rules",
          icon: "labelling-rules-view",
          condition: this.showLabellingRules,
        },
        { 
          type: 'metrics',
          id: "progress",
          tooltip: "Progress",
          icon: "progress"
        },
        {
          type: 'metrics',
          id: "stats",
          tooltip: "Stats",
          icon: "metrics"
        }
      ]
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
      return !this.dataset.isMultiLabel && this.dataset.task === 'TextClassification';
    }
  },
  watch: {
    viewMode(newValue) {
      this.currentViewMode = newValue;
    }
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
    showSidebarInfo(info) {
      this.$emit("showSidebarInfo", info);
      if (this.visibleSidebarInfo !== info) {
        this.visibleSidebarInfo = info;
      } else {
        this.visibleSidebarInfo = undefined;
      }
    },
    onChangeViewMode(id) {
      this.$emit('onChangeViewMode', id);
    },
  }
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
  .fixed-header & {
    top: 0;
  }
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
