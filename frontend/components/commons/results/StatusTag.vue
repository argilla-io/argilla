<template>
  <span :class="['status-tag', title]">
    <svgicon
      :name="
        title === 'Validated'
          ? 'check'
          : null || title === 'Edited'
          ? 'clock'
          : null || title === 'Discarded'
          ? 'forbidden'
          : null
      "
      width="12"
      height="12"
      color="#ffffff"
    ></svgicon>
    {{ title === "Edited" ? "Pending" : title }}
  </span>
</template>

<script>
import "assets/icons/check";
import "assets/icons/clock";
import "assets/icons/forbidden";
export default {
  props: {
    title: {
      type: String,
    },
  },
};
</script>

<style scoped lang="scss">
.status-tag {
  position: absolute;
  top: 1em;
  right: 3.6em;
  display: flex;
  align-items: center;
  background: $secondary-color;
  color: palette(white);
  border-radius: 50px;
  padding: 0.7em 1em;
  @include font-size(12px);
  font-weight: 600;
  z-index: 0;
  &.Edited {
    background: #bb720a;
  }
  &.Discarded {
    background: #70767f;
  }
  .svg-icon {
    margin-right: 0.5em;
  }
}
</style>
