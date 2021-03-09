<template>
  <div class="external-link">
    <NuxtLink target="_blank" :to="link">
      {{ title }}
    </NuxtLink>
    <svgicon name="external-link" width="12" height="12" />
  </div>
</template>

<script>
import "assets/icons/external-link";
export default {
  props: {
    link: {
      type: Object,
    },
    title: {
      type: String,
    },
  },
};
</script>

<style lang="scss" scoped>
.external-link,
.external-link a {
  position: relative;
  color: $primary-color;
  display: inline-block;
  margin-left: 1em;
  &:hover,
  &:focus {
    transition: $swift-ease-in-out;
    color: $primary-darken-color;
    .svg-icon {
      fill: $primary-darken-color;
    }
  }
  .svg-icon {
    margin-left: 0.5em;
  }
}
</style>
