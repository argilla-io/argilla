<template>
  <div class="tooltip-component">
    <span :data-title="message" :class="[tooltipDirection]">
      <slot>Here is the label of the tooltip</slot>
    </span>
  </div>
</template>

<script>
export default {
  name: "Tooltip",
  props: {
    message: {
      type: String,
      required: true,
    },
    direction: {
      type: String,
      required: true,
    },
  },
  computed: {
    tooltipDirection() {
      let tooltipDirection = "";
      switch (this.direction.toLowerCase()) {
        case "top":
          tooltipDirection = "top";
          break;
        case "right":
          tooltipDirection = "right";
          break;
        case "bottom":
          tooltipDirection = "bottom";
          break;
        case "left":
          tooltipDirection = "left";
          break;
        case "none":
          tooltipDirection = "";
          break;
      }
      return tooltipDirection;
    },
  },
};
</script>

<style lang="scss" scoped>
.tooltip-component > span {
  display: inline;
  position: relative;
  @extend %tooltip-large-text;
  cursor: pointer;
}
.top {
  @extend %has-tooltip--top;
}
.right {
  @extend %has-tooltip--right;
}
.bottom {
  @extend %has-tooltip--bottom;
}
.left {
  @extend %has-tooltip--left;
}
</style>
