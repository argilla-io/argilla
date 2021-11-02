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
        <a class="sidebar__info__button"
          href="#"
          data-title="Explore"
          @click="$emit('onEnableAnnotationView', false)"
        >
          <svgicon
            v-show="!annotationMode"
            class="sidebar__info__icon-help"
            name="check3"
          ></svgicon>
          <svgicon name="explore-view"></svgicon>
        </a>
        <a class="sidebar__info__button"
          href="#"
          data-title="Annotate"
          @click="$emit('onEnableAnnotationView', true)"
        >
          <svgicon
            v-show="annotationMode"
            class="sidebar__info__icon-help"
            name="check3"
          ></svgicon>
          <svgicon name="annotate-view"></svgicon>
        </a>
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
      annotationMode: false,
      width: window.innerWidth,
      visibleSidebarInfo: undefined,
      sidebarInfoOptions: [
        {
          id: "progress",
          tooltip: "Progress",
          icon: "progress"
        },
        {
          id: "stats",
          tooltip: "Stats",
          icon: "metrics"
        }
      ]
    };
  },
  computed: {
    annotationEnabled() {
      return this.isDatasetView && this.dataset.viewSettings.annotationEnabled;
    },
    isDatasetView() {
      return this.dataset !== undefined;
    }
  },
  watch: {
    annotationEnabled(newValue) {
      this.annotationMode = newValue;
    }
  },
  updated() {
    window.onresize = () => {
      this.width = window.innerWidth;
    };
  },
  mounted() {
    this.annotationMode = this.annotationEnabled;
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
    font-weight: 700;
    @include font-size(11px);
    color: $color;
  }
  a {
    position: relative;
    display: block;
    outline: none;
  }
  .svg-icon {
    display: block;
    text-align: center;
    margin: auto;
    width: 24px;
    height: 24px;
    margin-bottom: 1.5em;
    fill: $color;
  }
  &__info {
    position: relative;
    z-index: 1;
    margin-bottom: 5em;
    &__icon-help {
      left: 5px;
      width: 11px !important;
      margin-right: 0;
      stroke-width: 2;
      position: absolute;
      left: 0.8em;
    }
    &__button {
    }
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
