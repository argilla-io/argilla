<template>
  <transition name="re-progress" appear>
    <div class="re-progress">
      <div class="re-progress-track" :style="styles"></div>
      <div
        v-if="multiple && progressSecondary"
        class="re-progress-track--secondary"
        :style="stylesSecondary"
      />
    </div>
  </transition>
</template>

<script>
export default {
  props: {
    progress: {
      type: Number,
      default: 0,
    },
    progressSecondary: {
      type: Number,
      default: 0,
    },
    multiple: {
      default: false,
      type: Boolean,
    },
  },
  computed: {
    styles() {
      return {
        width: `${this.progress}%`,
      };
    },
    stylesSecondary() {
      return {
        left: `${this.progress}%`,
        width: `${this.progressSecondary}%`,
      };
    },
  },
};
</script>

<style lang="scss" scoped>
.re-progress {
  height: 10px;
  position: relative;
  overflow: hidden;
  background: #d1d0d3;
  border-radius: 2px;
  margin: 0 0 1.5em 0;
  &--minimal {
    @extend .re-progress;
    height: 2px;
    .re-progress-track {
      background: $line-medium-color;
    }
  }
  &--multiple {
    @extend .re-progress;
    height: 20px;
  }
}

.re-progress-track {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  transition: $swift-ease-out;
  border-bottom-left-radius: 2px;
  border-top-left-radius: 2px;
  background: $secondary-color;
  transition: $swift-ease-out;
  max-width: 100%;
  transition-duration: 2s;
  &:last-of-type {
    border-bottom-left-radius: 0;
    border-top-left-radius: 0;
  }
  .re-progress-enter-active & {
    max-width: 0;
  }
  &--secondary {
    @extend .re-progress-track;
    left: auto;
    right: 0;
    background: $error;
  }
}

@keyframes progress-indeterminate {
  0% {
    right: 100%;
    left: -35%;
  }
  60% {
    right: -100%;
    left: 100%;
  }
  100% {
    right: -100%;
    left: 100%;
  }
}

@keyframes progress-indeterminate-short {
  0% {
    right: 100%;
    left: -200%;
  }
  60% {
    right: -8%;
    left: 107%;
  }
  100% {
    right: -8%;
    left: 107%;
  }
}
</style>
