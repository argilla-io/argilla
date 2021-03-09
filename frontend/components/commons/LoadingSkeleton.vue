<template>
  <transition
    mode="in-out"
    :duration="{ enter: 0, leave: 500 }"
    name="skeleton"
    appear
  >
    <div v-if="condition" class="loading-skeleton">
      <span class="loading-skeleton__line" />
    </div>
  </transition>
</template>

<script>
import "assets/icons/drop-down";

export default {
  props: {
    itemsNumber: {
      type: Number,
      default: 10,
    },
    buttonsNumber: {
      type: Number,
      default: 4,
    },
    condition: {
      type: Boolean,
      default: false,
    },
  },
};
</script>

<style lang="scss" scoped>
.loading-skeleton {
  $this: &;
  background: $lighter-color !important;
  pointer-events: none;
  position: relative;
  min-height: 100vh;
  &__line {
    position: absolute;
    top: 0;
    height: 2px;
    display: block;
    background: lighten($secondary-color, 40%);
    animation: width 1s ease 0.5s infinite;
  }
}

@keyframes width {
  0% {
    width: 0;
  }
  100% {
    width: 100%;
  }
}
.skeleton-leave-active {
  .loading-skeleton__line {
    animation: width 1s ease 0s infinite;
  }
}
</style>
