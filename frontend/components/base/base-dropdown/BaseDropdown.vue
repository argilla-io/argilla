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
      handler: onClickOutside,
    }"
  >
    <div class="dropdown__header" @click="onClick">
      <slot name="dropdown-header" />
    </div>
    <transition appear name="fade">
      <div
        v-if="visible"
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
      dropdownTop: null,
      dropdownLeft: null,
    };
  },
  computed: {
    isViewportBoundary() {
      return this.boundary === "viewport";
    },
  },
  methods: {
    onClickOutside() {
      this.$emit("visibility", false);
    },
    onClick() {
      this.$emit("visibility", !this.visible);
      if (this.isViewportBoundary) {
        this.setViewportPosition();
        this.getScrollableParent(this.$refs.dropdown).addEventListener(
          "scroll",
          this.setViewportPosition
        );
      }
    },
    setViewportPosition() {
      return this.$nextTick(() => {
        const { top, left, height } =
          this.$refs.dropdown.getBoundingClientRect();
        this.dropdownTop = top + height + this.gap;
        this.dropdownLeft = left;
      });
    },
    isScrollable(el) {
      const hasScrollableContent =
        el.scrollHeight > el.clientHeight || el.scrollWidth > el.clientWidth;
      const overflowYStyle = window.getComputedStyle(el).overflow;
      const isOverflowHidden = overflowYStyle.indexOf("hidden") !== -1;
      return hasScrollableContent && !isOverflowHidden;
    },
    getScrollableParent(el) {
      return !el || el === document.body
        ? document.body
        : this.isScrollable(el)
        ? el
        : this.getScrollableParent(el.parentNode);
    },
  },
  mounted() {
    if (this.isViewportBoundary) {
      this.setViewportPosition();
      window.addEventListener("resize", this.setViewportPosition);
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
