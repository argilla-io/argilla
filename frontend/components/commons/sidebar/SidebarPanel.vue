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
        <div class="sidebar__close">
          <a
            href="#"
            @click.prevent="closePanel"
            :class="{ 'zoom-out': animated }"
            @animationend="animated = false"
            class="sidebar__close__button"
            ><svgicon name="chev-right" width="8"></svgicon
          ></a>
        </div>
        <slot></slot>
      </div>
    </div>
  </aside>
</template>
<script>
import "assets/icons/chev-right";
export default {
  data: () => {
    return {
      animated: false,
    };
  },
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  methods: {
    closePanel() {
      this.$emit("close-panel");
      this.animated = true;
    },
  },
};
</script>
<style lang="scss" scoped>
$topbarHeight: 56px;
$sidebarMenuWidth: 70px;
.sidebar {
  $this: &;
  min-height: calc(100vh - $topbarHeight);
  width: $sidebarPanelWidth;
  position: relative;
  top: 0;
  right: 0;
  background: $bg;
  padding: 1em 1.5em;
  transition: right 0.5s cubic-bezier(0.61, -0.08, 0.52, 1.17) 0.2s;
  // overflow: hidden;
  background: $bg;
  z-index: -1;
  border-left: 1px solid palette(grey, smooth);
  &__close {
    position: absolute;
    top: -2em;
    bottom: 0;
    left: -2.5em;
    width: 30px;
    min-height: 100vh;
    text-align: center;
    &:hover {
      #{$this}__close__button:not(.zoom-out) {
        opacity: 1;
        transform: scale(1);
        transition: transform 0.15s ease-in-out;
      }
    }
    &__button {
      margin-top: 2em;
      border-radius: 3px;
      background: palette(grey, smooth);
      display: flex;
      align-items: center;
      justify-content: center;
      width: 20px;
      height: 20px;
      transform: scale(0);
      overflow: hidden;
      transition: transform 0.2s ease-in;
      opacity: 0;
      outline: 0;
      &.zoom-out {
        opacity: 1;
        animation: zoom-out 0.3s ease-out forwards;
      }
    }
  }
  &__content {
    display: block;
    position: relative;
    opacity: 0;
    transition: opacity 0.1s ease-out 0.4s, transform 0.2s ease-in-out 0.2s;
    transform: translateX(5em);
    z-index: 0;
  }
  &.visible {
    overflow: visible;
    right: 0;
    transition: right 0.5s ease-in;
    .sidebar__content {
      transform: translateX(0);
      transition: opacity 0.1s ease-in-out 0.2s;
      opacity: 1;
    }
  }
  @include media(">desktop") {
    border-radius: 1px;
    margin-left: 1em;
    display: block !important;
    right: -$sidebarPanelWidth + 1px;
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
    }
  }
}

@keyframes zoom-out {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(0);
  }
  100% {
    transform: scale(0);
  }
}
</style>
