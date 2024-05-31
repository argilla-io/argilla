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
  <transition name="show-panel" appear>
    <aside class="sidebar">
      <div class="sidebar__content">
        <base-button
          @click.prevent="closePanel"
          :class="{ 'zoom-out': animated }"
          @animationend="animated = false"
          class="sidebar__close-button"
        >
          <svgicon name="chevron-right" width="12" height="12"></svgicon>
        </base-button>
        <transition name="fade" appear duration="500" mode="out-in">
          <slot></slot>
        </transition>
      </div>
    </aside>
  </transition>
</template>
<script>
import "assets/icons/chevron-right";
export default {
  data: () => {
    return {
      animated: false,
    };
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
  right: 0;
  background: palette(grey, 700);
  padding: 1em 1.5em 0 1.5em;
  border-left: 1px solid palette(grey, 600);
  overflow: visible;
  pointer-events: all;
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
    display: flex;
    overflow: hidden;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    padding: 0;
    background: palette(grey, 600);
    opacity: 0;
    outline: 0;
    border-radius: $border-radius-s;
    transform: scale(0);
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
    color: $black-54;
  }
  &__content {
    @include font-size(13px);
    &:first-child {
      padding-top: 0;
    }
  }
}

.show-panel-enter-active {
  animation: slide 0.4s ease-out;
}
.show-panel-leave-active {
  animation: slide 0.4s reverse ease-in;
}
.show-panel-enter-active {
  .sidebar__content {
    opacity: 0;
    animation: fade 0.2s ease-out 0.3s;
  }
}
.show-panel-leave-active {
  .sidebar__content {
    opacity: 0;
    animation: fade 0.1s reverse ease-in;
  }
}
@keyframes slide {
  0% {
    right: -$sidebarPanelWidth + 1px;
  }
  100% {
    right: 0;
  }
}
@keyframes fade {
  0% {
    opacity: 0;
  }
  100% {
    opacity: 1;
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
