<template>
  <span :class="['status-tag', title]">
    <svgicon
      :name="
        title === 'Validated'
          ? 'check'
          : null || title === 'Edited'
          ? 'time'
          : null || title === 'Discarded'
          ? 'unavailable'
          : null
      "
      width="16"
      height="16"
      color="#ffffff"
    ></svgicon>
    {{ title === "Edited" ? "Pending" : title }}
  </span>
</template>

<script>
import "assets/icons/check";
import "assets/icons/time";
import "assets/icons/unavailable";
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
  background: palette(blue, 200);
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
