<template>
    <span class="status-tag">
      <svgicon
        name="check"
        width="12"
        height="12"
        color="#ffffff"
      ></svgicon>
      {{title}}
    </span>
</template>

<script>
import "assets/icons/check";
export default {
  props: {
    title: {
      type: String
    }
  }
};
</script>

<style scoped lang="scss">
.status-tag {
  position: absolute;
  top: 4em;
  right: 2em;
  display: flex;
  align-items: center;
  background: $secondary-color;
  color: palette(white);
  border-radius: 50px;
  padding: 0.7em 1em;
  @include font-size(12px);
  font-weight: 600;
  z-index: 0;
  .svg-icon {
    margin-right: 0.5em;
  }
}
</style>

