<template>
  <div class="filter-tooltip">
    <slot></slot>
  </div>
</template>

<script>
export default {
  props: {
    text: {
      type: String,
    },
  },
  data() {
    return {
      clickable: false,
      clearable: false,
    };
  },
  mounted() {
    if (this.$listeners["on-click"]) {
      this.clickable = true;
    }
    if (this.$listeners["on-clear"]) {
      this.clearable = true;
    }
  },
  methods: {
    onClick($event) {
      this.$emit("on-click", $event);
    },
    onClear($event) {
      this.$emit("on-clear", $event);
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
  background: palette(white);
  border-radius: $border-radius;
  box-shadow: $shadow;
  z-index: 4;
  &:before {
    position: absolute;
    top: -$triangle-size;
    left: 0;
    right: 0;
    margin: auto;
    @include triangle(top, $triangle-size, $triangle-size, palette(white));
  }
}
</style>
