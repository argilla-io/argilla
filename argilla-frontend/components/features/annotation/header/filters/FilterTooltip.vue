<template>
  <div class="filter-tooltip__wrapper" ref="filterTooltip">
    <div
      class="filter-tooltip"
      ref="filterTooltipContent"
      :style="
        isViewportBoundary && {
          top: `${tooltipTop}px`,
          left: `${tooltipLeft}px`,
          right: 'auto',
          position: 'fixed',
          transform: 'none',
        }
      "
    >
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    text: {
      type: String,
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
      clickable: false,
      clearable: false,
      tooltipTop: null,
      tooltipLeft: null,
    };
  },
  computed: {
    isViewportBoundary() {
      return this.boundary === "viewport";
    },
  },
  mounted() {
    if (this.$listeners["on-click"]) {
      this.clickable = true;
    }
    if (this.$listeners["on-clear"]) {
      this.clearable = true;
    }
    if (this.isViewportBoundary) {
      this.setViewportPosition();
      window.addEventListener("resize", this.setViewportPosition);
    }
  },
  beforeDestroy() {
    if (this.isViewportBoundary) {
      window.removeEventListener("resize", this.setViewportPosition);
    }
  },
  methods: {
    onClick($event) {
      this.$emit("on-click", $event);
    },
    onClear($event) {
      this.$emit("on-clear", $event);
    },
    setViewportPosition() {
      return this.$nextTick(() => {
        const contentWidth =
          this.$refs.filterTooltipContent.getBoundingClientRect().width;
        const { top, left, height, width } =
          this.$refs.filterTooltip.getBoundingClientRect();
        this.tooltipTop = top + height + this.gap;
        this.tooltipLeft = left - contentWidth / 2 + width / 2;
      });
    },
  },
};
</script>

<style lang="scss" scoped>
$triangle-size: 6px;
.filter-tooltip {
  position: absolute;
  top: calc(100% + $base-space + $triangle-size);
  right: 50%;
  transform: translateX(50%);
  padding: $base-space * 2;
  background: var(--bg-accent-grey-3);
  border-radius: $border-radius;
  box-shadow: $shadow;
  z-index: 4;
  &:before {
    position: absolute;
    top: -$triangle-size;
    left: 0;
    right: 0;
    margin: auto;
    @include triangle(
      top,
      $triangle-size,
      $triangle-size,
      var(--bg-accent-grey-3)
    );
  }
}
</style>
