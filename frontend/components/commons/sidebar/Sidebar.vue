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
    <div class="sidebar__actions">
      <a
        v-if="$auth.loggedIn"
        href="#"
        data-title="close session"
        @click.prevent="logout()"
      >
        <svgicon name="logout"></svgicon>
      </a>
      <a href="#" data-title="refresh" @click.prevent="$emit('refresh')">
        <svgicon name="refresh"></svgicon>
      </a>
      <a
        v-if="isDatasetView"
        href="#"
        data-title="annotation mode"
        @click="$emit('onChangeMode')"
      >
        <svgicon
          :class="annotationMode ? 'active' : 'inactive'"
          name="editable"
        ></svgicon>
      </a>
    </div>
    <div v-if="isDatasetView" class="sidebar__info">
      <a
        v-for="sidebarInfo in sidebarInfoOptions"
        :key="sidebarInfo.id"
        class="sidebar__info__button"
        href="#"
        :data-title="sidebarInfo.tooltip"
        :class="visibleSidebarInfo === sidebarInfo.id ? 'active' : ''"
        @click.prevent="showSidebarInfo(sidebarInfo.id)"
      >
        <svgicon
          class="sidebar__info__chev"
          :name="
            visibleSidebarInfo === sidebarInfo ? 'chev-right' : 'chev-left'
          "
        ></svgicon>
        <svgicon :name="sidebarInfo.icon"></svgicon>
      </a>
    </div>
  </div>
</template>

<script>
import "assets/icons/logout";
import "assets/icons/refresh";
import "assets/icons/editable";
import "assets/icons/progress";
import "assets/icons/metrics";
import "assets/icons/chev-left";
import "assets/icons/chev-right";
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
      annotationMode: false,
      width: window.innerWidth,
      visibleSidebarInfo: undefined,
      sidebarInfoOptions: [
        {
          id: "progress",
          tooltip: "annotation progress",
          icon: "progress",
        },
        {
          id: "stats",
          tooltip: "stats",
          icon: "metrics",
        },
      ],
    };
  },
  computed: {
    annotationEnabled() {
      return this.isDatasetView && this.dataset.viewSettings.annotationEnabled;
    },
    isDatasetView() {
      return this.dataset !== undefined;
    },
  },
  watch: {
    annotationEnabled(newValue) {
      this.annotationMode = newValue;
    },
  },
  updated() {
    window.onresize = () => {
      this.width = window.innerWidth;
    };
  },
  mounted() {
    if (this.width > 1500) {
      this.visibleSidebarInfo = "progress";
    }
    this.annotationMode = this.annotationEnabled;
  },
  methods: {
    showSidebarInfo(info) {
      this.visibleSidebarInfo = info;
      this.$emit("showSidebarInfo", info);
    },
    async logout() {
      await this.$auth.logout();
      await this.$auth.strategy.token.reset();
    },
  },
};
</script>

<style lang="scss" scoped>
$sidebar-button-size: 45px;
.sidebar {
  position: fixed;
  top: 0;
  right: 0;
  background: palette(grey, verylight);
  width: $sidebar-button-size;
  min-width: $sidebar-button-size;
  min-height: 100vh;
  z-index: 2;
  a {
    position: relative;
  }
  .svg-icon {
    fill: $primary-color;
    display: block;
    height: $sidebar-button-size;
    text-align: center;
    line-height: $sidebar-button-size;
    margin: auto;
    &.inactive {
      opacity: 0.15;
    }
  }
  &__actions {
    margin-bottom: 3.8em;
    &__switch {
      margin: 1em auto;
    }
  }
  &__info {
    &__chev {
      left: 5px;
      width: 5px;
      margin-right: 0;
      stroke-width: 2;
    }
    .svg-icon {
      & + .svg-icon {
        margin-right: auto;
        margin-left: 0;
      }
    }
    &__button {
      display: flex;
      &.active {
        background: white;
        outline: none;
      }
    }
  }
}
a[data-title] {
  @extend %hastooltip;
  &:after {
    top: 1em;
    right: calc(100% - 5px);
    transform: none;
    background: $font-secondary-dark;
    color: white;
    border: none;
  }
}
</style>
