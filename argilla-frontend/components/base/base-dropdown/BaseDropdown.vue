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
    <div
      @click="onClose"
      v-if="visible && freezingPage"
      class="dropdown--frozen-page"
    ></div>
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
    freezingPage: {
      type: Boolean,
      default: false,
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
      frozenScrollParent: null,
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
    freezingPage(value) {
      if (value) {
        this.frozenScrollParent = this.getScrollableParent(this.$refs.dropdown);
        this.frozenScrollParent.style.overflow = "hidden";
      } else {
        this.frozenScrollParent.style.overflow = "auto";
      }
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
    getScrollableParent(element) {
      if (!element) {
        return undefined;
      }

      let parent = element.parentElement;
      while (parent) {
        const { overflow } = window.getComputedStyle(parent);
        if (overflow.split(" ").every((o) => o === "auto" || o === "scroll")) {
          return parent;
        }
        parent = parent.parentElement;
      }

      return document.documentElement;
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
  color: var(--fg-secondary);
  &__header {
    display: flex;
    align-items: center;
    transition: all 0.2s ease;
    border-radius: $border-radius;
    &:hover,
    &:focus {
      border-color: var(--fg-tertiary);
      background: var(--bg-accent-grey-2);
      transition: all 0.3s ease;
      &:after {
        color: var(--fg-secondary);
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
    background: var(--bg-accent-grey-2);
  }
  &--frozen-page {
    &:before {
      content: "";
      position: fixed;
      height: 100vh;
      width: 100vw;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      z-index: 2;
    }
  }
}
</style>
