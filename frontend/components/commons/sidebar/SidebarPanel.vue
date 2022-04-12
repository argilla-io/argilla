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
  <aside class="sidebar">
    <div class="sidebar__wrapper">
      <div class="sidebar__content">
        <svgicon
          @click="closePanel"
          class="sidebar__panel__button"
          name="chev-right"
        ></svgicon>
        <slot></slot>
      </div>
    </div>
  </aside>
</template>
<script>
import "assets/icons/chev-right";
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  methods: {
    closePanel() {
      this.$emit("close-panel");
    },
  },
};
</script>
<style lang="scss" scoped>
$topbarHeight: 56px;
$sidebarMenuWidth: 70px;
.sidebar {
  top: 0;
  min-height: calc(100vh - $topbarHeight);
  width: $sidebarPanelWidth;
  position: absolute;
  right: -$sidebarPanelWidth;
  background: $bg;
  padding: 1em 1.5em;
  transition: right 0.5s cubic-bezier(0.61, -0.08, 0.52, 1.17),
    box-shadow 0.1s ease-out;
  box-shadow: none;
  overflow: hidden;
  background: $bg;
  .sidebar__content {
    display: block;
    position: relative;
    opacity: 0;
    transition: opacity 0.3s ease-out, transform 0.2s ease-in-out;
    transform: translateX(5em);
  }
  &.visible {
    overflow: visible;
    box-shadow: -4px 15px 16px -1px #c7c7c7;
    right: $sidebarMenuWidth;
    transition: right 0.5s ease-in-out, box-shadow 0.4s ease-in-out 0.6s;
    .sidebar__content {
      transform: translateX(0);
      transition: opacity 0.2s ease-in-out 0.3s;
      opacity: 1;
    }
  }
  @include media(">desktop") {
    border-radius: 1px;
    border: none;
    margin-left: 1em;
    display: block !important;
    right: -$sidebarPanelWidth;
  }
  &__panel {
    &__button {
      position: absolute;
      left: 0;
      top: 0.2em;
      pointer-events: all;
      cursor: pointer;
      z-index: 2;
      border-radius: 3px;
      padding: 5px;
      background: palette(grey, smooth);
      box-sizing: content-box;
      max-width: 8px;
      max-height: 8px;
      transform: translateX(-2em);
      transition: transform 0.2s ease-in-out;
      &:hover {
        background: darken(palette(grey, smooth), 5%);
      }
      .visible & {
        transform: translateX(0);
        transition: transform 0.2s ease-in-out 0.4s;
      }
    }
  }
  &__content {
    border-radius: 2px;
    @include font-size(13px);
    &:first-child {
      padding-top: 0;
    }
  }
  ::v-deep {
    .sidebar__title {
      margin-bottom: 2em;
      margin-left: 1.5em;
    }
  }
}
.visible ::v-deep .sidebar--animation {
  @for $i from 1 through 40 {
    & > *:nth-child(#{$i}) {
      animation: move-horizontal 0.2s ease-in-out #{0.4 + $i * 0.05}s;
      animation-fill-mode: backwards;
    }
  }
}

@keyframes move-horizontal {
  0% {
    transform: translateX(1.5em);
    opacity: 0;
  }
  100% {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
