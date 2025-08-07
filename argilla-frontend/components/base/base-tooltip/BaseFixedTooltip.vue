<template>
  <div
    v-if="isVisible"
    role="tooltip"
    class="fixed-tooltip"
    ref="tooltip"
    v-click-outside="closeTooltip"
    :style="{ top: `${top}px`, left: `${left}px` }"
  >
    <div class="fixed-tooltip__content" :class="isSmallTooltip">
      <span v-html="content" />
      <BaseButton
        @click.native.stop="closeTooltip"
        class="fixed-tooltip__button"
      >
        <svgicon name="close" width="12" />
      </BaseButton>
    </div>
  </div>
</template>

<script>
import "assets/icons/close";
export default {
  props: {
    content: {
      type: String,
      required: true,
    },
    open: {
      type: Boolean,
      default: false,
    },
    triggerElement: {
      type: HTMLButtonElement,
      required: true,
    },
  },
  data() {
    return {
      top: 0,
      left: 0,
      isVisible: false,
    };
  },
  computed: {
    isSmallTooltip() {
      return this.content.length < 40 ? "--small" : null;
    },
  },
  methods: {
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
    scrollInParent() {
      const { top: parentOffsetTop = 0, bottom: parentOffsetBottom = 0 } =
        this.getScrollableParent(this.triggerElement).getBoundingClientRect() ||
        {};
      const { top: elementOffsetTop = 0, bottom: elementOffsetBottom = 0 } =
        this.triggerElement.getBoundingClientRect() || {};
      if (this.$refs.tooltip) {
        if (
          elementOffsetTop < parentOffsetTop ||
          elementOffsetBottom > parentOffsetBottom
        ) {
          this.$refs.tooltip.style.visibility = "hidden";
        } else {
          this.$refs.tooltip.style.visibility = "visible";
        }
        this.updatePosition();
      }
    },
    updatePosition() {
      this.$nextTick(() => {
        const tooltipWidth = this.$refs.tooltip?.offsetWidth;
        if (!tooltipWidth) {
          return;
        }
        const rect = this.triggerElement.getBoundingClientRect();
        this.top =
          rect.top + window.scrollY + this.triggerElement.offsetHeight + 10;
        this.left =
          rect.left + window.scrollX - tooltipWidth / 2 + rect.width / 2;
      });
    },
    toggleTooltip() {
      this.isVisible = !this.isVisible;
      this.updatePosition();
    },
    closeTooltip() {
      if (this.isVisible) {
        this.isVisible = false;
      }
    },
  },
  mounted() {
    this.isVisible = this.open;
    this.$nextTick(() => {
      this.getScrollableParent(this.triggerElement).addEventListener(
        "scroll",
        this.scrollInParent
      );
      window.addEventListener("resize", this.updatePosition);
      this.triggerElement.addEventListener("click", this.toggleTooltip);
      this.updatePosition();
    });
  },
  beforeDestroy() {
    this.getScrollableParent(this.triggerElement).removeEventListener(
      "scroll",
      this.scrollInParent
    );
    window.removeEventListener("resize", this.updatePosition);
    this.triggerElement.removeEventListener("click", this.toggleTooltip);
  },
};
</script>

<style scoped lang="scss">
$tooltip-triangle-size: 10px;
$tooltip-bg: var(--bg-tooltip);
$tooltip-color: var(--color-white);
$tooltip-border-radius: $border-radius-s;
$tooltip-max-width: 400px;
$tooltip-small-max-width: 100px;

.fixed-tooltip {
  position: fixed;
  z-index: 3;
  &__content {
    position: relative;
    width: 100%;
    max-width: $tooltip-max-width;
    background-color: $tooltip-bg;
    color: $tooltip-color;
    padding: $base-space $base-space * 3 $base-space $base-space;
    border-radius: $tooltip-border-radius;
    box-shadow: 0 8px 20px 0 rgba(0, 0, 0, 0.2);
    text-align: left;
    font-weight: 300;
    white-space: pre-wrap;
    overflow: auto;
    max-height: 360px;
    @include line-height(18px);
    @include font-size(13px);
    cursor: default;
    &.--small {
      max-width: $tooltip-small-max-width;
    }
    :deep(a) {
      outline: none;
      color: $tooltip-color;
    }
  }
  &__button {
    position: absolute;
    top: calc($base-space / 2);
    right: calc($base-space / 2);
    background: transparent;
    padding: 0;
    color: $tooltip-color;
    cursor: pointer;
  }
  &:before {
    position: absolute;
    left: calc(50% - $tooltip-triangle-size);
    transform: translateY(-50%);
    bottom: calc(100% - $tooltip-triangle-size / 2);
    @include triangle(
      top,
      $tooltip-triangle-size,
      $tooltip-triangle-size,
      $tooltip-bg
    );
  }
}
</style>
