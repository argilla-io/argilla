<template>
  <div v-if="showAnnotationMode" class="container">
    <div class="global-actions">
      <slot />
    </div>
  </div>
</template>
<script>
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data: () => ({}),
  computed: {
    showAnnotationMode() {
      return this.dataset.viewSettings.annotationEnabled;
    },
  },
};
</script>
<style lang="scss">
.container {
  @extend %container;
  padding-top: 0;
  padding-bottom: 0;
}

.global-actions {
  display: flex;
  align-items: center;
  width: 100%;
  text-align: left;
  padding: 1em 1.4em;
  background: $lighter-color;
  border-radius: 3px;
  position: relative;
  &--exploration {
    position: relative;
  }
  .fixed-header & {
    margin-top: 0;
    padding-top: 0;
    padding-bottom: 0;
    background: $bg;
    border: none;
    min-height: 70px;
  }
  @include media(">desktopLarge") {
    width: calc(100% - 294px);
  }
  .re-checkbox {
    position: relative;
    left: 0;
    top: 0;
    margin: 0 8px 0 0;
  }
  &__export {
    margin: auto 0 auto auto;
  }
  &__select {
    margin-left: 0.8em;
    ::v-deep .dropdown__header {
      border-radius: 5px;
      max-height: 33px;
      background: $lighter-color;
      border-width: 1px;
      color: $font-secondary;
      font-weight: bold;
    }
  }
  &__button {
    border-radius: 5px;
    height: 33px;
    border: none;
    min-width: 80px;
    margin-left: 1em;
    margin-right: 1em;
    outline: none;
    font-weight: 600;
    color: $font-secondary;
    background: $lighter-color;
    border: 1px solid $line-smooth-color;
    cursor: pointer;
    &:hover,
    &:focus {
      border-color: $primary-color;
    }
    &:first-of-type {
      margin-right: 0;
    }
  }
  &__text {
    color: $darker-color;
    font-weight: normal;
  }
  &--disabled {
    .global-actions__button,
    .global-actions__select {
      pointer-events: none;
      opacity: 0.5;
    }
  }
}
</style>
