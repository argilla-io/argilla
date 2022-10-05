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
  background: palette(grey, 700);
  padding: 1em 1.5em;
  transition: right 0.25s linear 0.2s;
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
    border-radius: $border-radius-s;
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
    color: $black-54;
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
    margin-left: 1em;
    display: block !important;
    right: -$sidebarPanelWidth + 1px;
  }
  &__content {
    @include font-size(13px);
    &:first-child {
      padding-top: 0;
    }
  }
  :deep() {
    .metrics__title {
      margin-top: 0;
      margin-bottom: $base-space * 4;
      @include font-size(18px);
      font-weight: 600;
    }
    .metrics__subtitle {
      @include font-size(15px);
      font-weight: 600;
    }
    .metrics__info {
      margin-top: 0;
      margin-bottom: $base-space;
      display: flex;
      &__name {
        margin: 0;
      }
      &__counter {
        margin: 0 0 0 auto;
      }
      & + .re-progress__container {
        margin-top: -$base-space;
      }
    }
    .metrics__list {
      list-style: none;
      padding-left: 0;
      margin-bottom: $base-space * 3;
      li {
        display: flex;
        align-items: center;
        margin-bottom: $base-space;
        @include font-size(13px);
      }
      &__name {
        display: block;
        width: calc(100% - 40px);
        hyphens: auto;
        word-break: break-word;
      }
      &__counter {
        margin-right: 0;
        margin-left: auto;
      }
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
