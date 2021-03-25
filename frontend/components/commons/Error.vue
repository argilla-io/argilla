<template>
  <div class="error">
    <div class="panel panel--warning">
      <p class="panel__title">Warning</p>
      <p class="panel__text">
        We cannot currently access <strong>{{ where }}</strong> due to the
        following error: <strong>{{ error.message }}</strong>
      </p>
    </div>
    <NuxtLink class="re-button" :to="link">
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
      type: String,
      default: undefined,
    },
    error: {
      type: Object,
      default: undefined,
    },
  },
};
</script>

<style lang="scss" scoped>
.error {
  margin-left: 10vw;
  text-align: left;
}
.panel {
  $this: &;
  position: relative;
  max-width: 700px;
  border: 1px solid $line-smooth-color;
  color: $neutral-color;
  border-radius: 3px;
  padding: 1.2em 5em 1.2em 1.2em;
  @include font-size(14px);
  line-height: 1.5em;
  margin-bottom: 2em;
  text-align: left;
  overflow: hidden;
  &__text {
    margin: 0;
  }
  &.hidden {
    margin: 0;
    padding: 0;
    min-height: 0;
    opacity: 0;
    transition: opacity 0.1s ease-in-out, height 0.3s ease-in-out,
      margin 0.3s ease-in-out, padding 0.3s ease-in-out;
  }
  &--inline,
  &--inline p {
    display: inline-block;
  }
  &--inline {
    margin-bottom: 1em;
    padding: 1em;
  }
  &--block {
    margin-bottom: 1em;
    padding: 1em;
  }
  &--warning {
    margin-top: 5em;
    background: $lighter-color;
    border: 1px solid $error;
    max-width: calc(100% - 320px);
    #{$this}__title {
      color: $error;
      font-weight: 600;
      margin-top: 0;
      @include font-size(16px)
    }
  }
}

.re-button {
  display: inline-block;
  min-height: 40px;
  line-height: 40px;
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
  text-decoration: none;
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
