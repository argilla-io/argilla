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
        <a
          href="#"
          @click.prevent="closePanel"
          :class="{ 'zoom-out': animated }"
          @animationend="animated = false"
          class="sidebar__close-button"
          ><svgicon name="chevron-right" width="12" height="12"></svgicon
        ></a>
        <slot></slot>
      </div>
    </div>
  </aside>
</template>
<script>
import "assets/icons/chevron-right";
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
.sidebar {
  $this: &;
  width: $sidebarPanelWidth;
  position: relative;
  top: 0;
  right: -$sidebarPanelWidth + 1px;
  background: $bg;
  padding: 1em 1.5em;
  transition: right 0.25s linear 0.2s;
  z-index: -1;
  border-left: 1px solid palette(grey, 600);
  &:hover {
    #{$this}__close-button:not(.zoom-out) {
      opacity: 1;
      transform: scale(1);
      transition: transform 0.15s ease-in-out;
    }
  }
  &__close-button {
    position: absolute;
    left: -2.5em;
    top: 1px;
    border-radius: 3px;
    background: palette(grey, 600);
    display: flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    transform: scale(0);
    overflow: hidden;
    opacity: 0;
    outline: 0;
    &.zoom-out {
      opacity: 1;
      animation: zoom-out 0.3s ease-out forwards;
    }
    .svg-icon {
      color: palette(blue, 300);
    }
  }
  &__content {
    display: block;
    position: relative;
    opacity: 0;
    transition: opacity 0.1s ease-out 0.6s;
    z-index: 0;
  }
  &.visible {
    overflow: visible;
    right: 0;
    transition: right 0.25s linear;
    .sidebar__content {
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
  :deep() {
    .sidebar__title {
      margin-bottom: 2em;
      color: $font-secondary-medium-dark;
      margin-top: 0.2em;
      @include font-size(20px);
      font-weight: 700;
    }
    .sidebar__subtitle {
      @include font-size(15px);
      color: $font-secondary-medium-dark;
      font-weight: 600;
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
