<template>
  <div>
    <div class="panel panel--warning">
      <p class="panel__title">Warning</p>
      <p class="panel__text">
        We cannot currently access <strong>{{ where }}</strong> due to the
        following error: <strong>{{ error }}</strong>
      </p>
    </div>
    <NuxtLink class="re-button button-secondary" :to="link">
      <svgicon name="chev-left" width="15" height="15" color="#4A4A4A" />
      Back
    </NuxtLink>
  </div>
</template>

<script>
import "assets/icons/chev-left";

export default {
  props: {
    where: {
      type: String,
      default: undefined,
    },
    link: {
      type: Object,
      default: undefined,
    },
    error: {
      type: Error,
      default: undefined,
    },
  },
};
</script>

<style lang="scss" scoped>
// @import "@recognai/re-commons/src/assets/scss/components/panel.scss";
// @import "@recognai/re-commons/src/assets/scss/components/buttons.scss";
.re-button {
  min-height: 40px;
  min-width: 150px;
  background: transparent;
  text-align: center;
  border: 1px solid $font-medium-color;
  padding: 0 2em;
  position: relative;
  font-weight: 600;
  color: $font-medium-color;
  border-radius: 3px;
  margin-bottom: 20vh;
  text-transform: none;
  &:hover {
    color: darken($font-medium-color, 10%);
  }
  .svg-icon {
    position: absolute;
    left: 12px;
    top: 12px;
  }
}
</style>
