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
  <div
    ref="dropdown"
    class="dropdown"
    v-click-outside="{
      events: ['mousedown'],
      handler: onClose,
    }"
  >
    <div class="dropdown__header" @click="onClick">
      <slot name="dropdown-header" />
    </div>
    <transition appear name="fade">
      <div
        v-if="visible && inViewport"
        class="dropdown__content"
        :style="
          isViewportBoundary && {
            top: `${dropdownTop}px`,
            left: `${dropdownLeft}px`,
            position: 'fixed',
          }
        "
      >
        <slot name="dropdown-content" />
      </div>
    </transition>
  </div>
</template>
<script>
import ClickOutside from "v-click-outside";
export default {
  directives: {
    clickOutside: ClickOutside.directive,
  },
  props: {
    visible: {
      type: Boolean,
      default: false,
    },
    boundary: {
      type: String,
      default: "parent",
      validator: (value) => ["parent", "viewport"].includes(value),
    },
    gap: {
      type: Number,
      default: 8,
    },
  },
  data() {
    return {
      dropdownTop: 0,
      dropdownLeft: 0,
      inViewport: true,
    };
  },
  computed: {
    isViewportBoundary() {
      return this.boundary === "viewport";
    },
  },
  watch: {
    visible() {
      this.$nextTick(() => {
        this.setViewportPosition();
      });
    },
  },
  methods: {
    onClose() {
      this.$emit("visibility", false);
    },
    onToggle() {
      this.$emit("visibility", !this.visible);
    },
    onClick() {
      this.onToggle();
    },
    setViewportPosition() {
      if (!this.isViewportBoundary) return;
      if (!this.visible) return;

      this.inViewport = this.isInViewport(this.$refs.dropdown);

      if (!this.inViewport) return;

      const { top, left, height } = this.$refs.dropdown.getBoundingClientRect();

      this.dropdownTop = top + height + this.gap;

      this.dropdownLeft = left;
    },
    isScrollable(el) {
      const hasScrollableContent =
        el.scrollHeight > el.clientHeight || el.scrollWidth > el.clientWidth;
      const overflowYStyle = window.getComputedStyle(el).overflow;
      const isOverflowHidden = overflowYStyle.indexOf("hidden") !== -1;
      return hasScrollableContent && !isOverflowHidden;
    },
    getScrollableParent(element) {
      const isBody = !element || element === document.body;

      if (isBody) return document.body;

      if (this.isScrollable(element)) return element;

      return this.getScrollableParent(element.parentNode);
    },
    isInViewport(element) {
      const rect = element.getBoundingClientRect();
      const parentHeight = element.offsetHeight;

      const html = document.documentElement;
      return (
        rect.top >= parentHeight &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || html.clientHeight) &&
        rect.right <= (window.innerWidth || html.clientWidth)
      );
    },
  },
  mounted() {
    if (this.isViewportBoundary) {
      window.addEventListener("resize", this.setViewportPosition);
      this.getScrollableParent(this.$refs.dropdown).addEventListener(
        "scroll",
        this.setViewportPosition
      );

      this.setViewportPosition();
    }
  },
  beforeDestroy() {
    if (this.isViewportBoundary) {
      window.removeEventListener("resize", this.setViewportPosition);
      this.getScrollableParent(this.$refs.dropdown).removeEventListener(
        "scroll",
        this.setViewportPosition
      );
    }
  },
};
</script>

<style lang="scss" scoped>
.dropdown {
  position: relative;
  color: $black-54;
  &__header {
    display: flex;
    align-items: center;
    transition: all 0.2s ease;
    border-radius: $border-radius;
    &:hover,
    &:focus {
      border-color: $black-37;
      background: palette(white);
      transition: all 0.3s ease;
      &:after {
        border-color: $black-54;
      }
    }
  }
  &__content {
    position: absolute;
    top: calc(100% + 8px);
    left: 0;
    z-index: 3;
    transform: translate(0);
    box-shadow: $shadow;
    border-radius: $border-radius;
    background: palette(white);
  }
}
</style>
