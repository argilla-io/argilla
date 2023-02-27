<template>
  <span :class="['status-tag', title]">
    <svgicon
      :name="
        title === 'Validated'
          ? 'validate'
          : null || title === 'Edited'
          ? 'time'
          : null || title === 'Discarded'
          ? 'discard'
          : null
      "
      width="14"
      height="14"
      color="#ffffff"
    ></svgicon>
    {{ title === "Edited" ? "Pending" : title }}
  </span>
</template>

<script>
import "assets/icons/validate";
import "assets/icons/time";
import "assets/icons/discard";
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
  display: inline-flex;
  align-items: center;
  margin-left: 1.7em;
  background: palette(green);
  color: palette(white);
  border-radius: 50px;
  padding: 0.2em 1em;
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
