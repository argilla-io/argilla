<!--
  - coding=utf-8
  - Copyright 2021-present, the Recognai S.L. team.
  -
  - Licensed under the Apache License, Version 2.0 (the "License");
  - you may not use this file except in compliance with the License.
  - You may obtain a copy of the License at
  -
  -     http://www.apache.org/licenses/LICENSE-2.0
  -
  - Unless required by applicable law or agreed to in writing, software
  - distributed under the License is distributed on an "AS IS" BASIS,
  - WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  - See the License for the specific language governing permissions and
  - limitations under the License.
  -->

<template>
  <transition
    :enter-active-class="transition.enter"
    :leave-active-class="transition.leave"
  >
    <div
      v-show="isActive"
      role="alert"
      class="toast"
      :class="[`toast-${type}`, `is-${position}`]"
      @mouseover="toggleTimer(true)"
      @mouseleave="toggleTimer(false)"
    >
      <div class="toast-icon"></div>
      <p class="toast-text" v-html="message"></p>
      <span v-if="buttonText" class="toast__button" @click="whenClicked">{{
        buttonText
      }}</span>
      <span class="toast__close" @click="close()"></span>
    </div>
  </transition>
</template>

<script>
import { removeElement } from "./helpers";
import Timer from "./timer";
import Positions from "./positions";
import eventBus from "./bus";

export default {
  name: "Toast",
  props: {
    message: {
      type: [String, Error],
      required: true,
    },
    type: {
      type: String,
      default: "success",
    },
    buttonText: {
      type: String,
      default: undefined,
    },
    position: {
      type: String,
      default: Positions.BOTTOM_RIGHT,
      validator(value) {
        return Object.values(Positions).includes(value);
      },
    },
    duration: {
      type: Number,
      default: 10000,
    },
    dismissible: {
      type: Boolean,
      default: true,
    },
    replaceToast: {
      type: Boolean,
      default: false,
    },
    onClose: {
      type: Function,
      default: () => {},
    },
    onClick: {
      type: Function,
      default: () => {},
    },
    queue: Boolean,
    pauseOnHover: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      isActive: false,
      parentTop: null,
      parentBottom: null,
      isHovered: false,
    };
  },
  computed: {
    correctParent() {
      switch (this.position) {
        case Positions.TOP:
        case Positions.TOP_RIGHT:
        case Positions.TOP_LEFT:
          return this.parentTop;
        case Positions.BOTTOM:
        case Positions.BOTTOM_RIGHT:
        case Positions.BOTTOM_LEFT:
          return this.parentBottom;
        default:
          return this.parentTop;
      }
    },
    transition() {
      switch (this.position) {
        case Positions.TOP:
        case Positions.TOP_RIGHT:
        case Positions.TOP_LEFT:
          return {
            enter: "fadeInDown",
            leave: "fadeOut",
          };
        case Positions.BOTTOM:
        case Positions.BOTTOM_RIGHT:
        case Positions.BOTTOM_LEFT:
          return {
            enter: "fadeInUp",
            leave: "fadeOut",
          };
        default:
          return {
            enter: "fadeInDown",
            leave: "fadeOut",
          };
      }
    },
  },
  beforeMount() {
    this.setupContainer();
  },
  mounted() {
    this.showNotice();
    eventBus.$on("toast.clear", this.close);
  },
  beforeDestroy() {
    eventBus.$off("toast.clear", this.close);
  },
  methods: {
    setupContainer() {
      this.parentTop = document.querySelector(".notices.is-top");
      this.parentBottom = document.querySelector(".notices.is-bottom");
      // No need to create them, they already exists
      if (this.parentTop && this.parentBottom) return;
      if (!this.parentTop) {
        this.parentTop = document.createElement("div");
        this.parentTop.className = "notices is-top";
      }
      if (!this.parentBottom) {
        this.parentBottom = document.createElement("div");
        this.parentBottom.className = "notices is-bottom";
      }
      const container = document.body;
      container.appendChild(this.parentTop);
      container.appendChild(this.parentBottom);
    },
    shouldQueue() {
      if (!this.queue) return false;
      return (
        this.parentTop.childElementCount > 0 ||
        this.parentBottom.childElementCount > 0
      );
    },
    close(...arg) {
      this.timer.stop();
      clearTimeout(this.queueTimer);
      this.isActive = false;
      // Timeout for the animation complete before destroying
      setTimeout(() => {
        this.onClose.apply(null, arg);
        this.$destroy();
        removeElement(this.$el);
      }, 150);
    },
    showNotice() {
      if (this.shouldQueue()) {
        // Call recursively if should queue
        this.queueTimer = setTimeout(this.showNotice, 250);
        return;
      }
      if (!this.replaceToast) {
        this.correctParent.insertAdjacentElement("afterbegin", this.$el);
      } else {
        if (this.correctParent.hasChildNodes()) {
          this.correctParent.removeChild(this.correctParent.childNodes[0]);
        }
        this.correctParent.insertAdjacentElement("afterbegin", this.$el);
      }
      this.isActive = true;
      this.timer = new Timer(this.close, this.duration);
    },
    whenClicked(...arg) {
      if (!this.dismissible) return;
      this.onClick.apply(null, arg);
      this.close();
    },
    toggleTimer(newVal) {
      if (!this.pauseOnHover) return;
      if (newVal) {
        this.timer.pause();
      } else {
        this.timer.resume();
      }
    },
  },
};
</script>
<style lang="scss">
$toast-colors: () !default;
$toast-colors: map-merge(
  (
    "success": $success,
    "info": $info,
    "warning": $warning,
    "error": $error,
  ),
  $toast-colors
);
.notices {
  position: fixed;
  display: flex;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 2em;
  overflow: hidden;
  z-index: 1052;
  pointer-events: none;

  // Colors
  @each $color, $value in $toast-colors {
    .toast-#{$color} {
      border: 2px solid $value;
    }
  }

  // Individual toast position
  .toast {
    &.is-top,
    &.is-bottom {
      align-self: center;
    }
    &.is-top-right,
    &.is-bottom-right {
      align-self: flex-end;
    }
    &.is-top-left,
    &.is-bottom-left {
      align-self: flex-start;
    }
  }

  // Notice container positions
  &.is-top {
    flex-direction: column;
  }
  &.is-bottom {
    flex-direction: column-reverse;
  }
  &.is-custom-parent {
    position: absolute;
  }
}
.toast {
  $this: &;
  display: inline-flex;
  align-items: center;
  animation-duration: 150ms;
  margin: 0.5em 0;
  box-shadow: $shadow;
  border-radius: 0.25em;
  pointer-events: auto;
  color: $darker-color;
  background: $lighter-color !important;
  min-height: 3em;
  .toast-text {
    margin: 0;
    padding: 1.5em;
  }
  &__button {
    color: $secondary-color;
    margin: 0 3em;
    cursor: pointer;
  }
  &__close {
    margin-right: 1em;
    cursor: pointer;
    &:after {
      content: "\2573";
      color: $darker-color;
      font-size: 10px;
    }
  }
}
// Animations are taken from animate.css
// https://daneden.github.io/animate.css

@keyframes fadeOut {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}

.fadeOut {
  animation-name: fadeOut;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translate3d(0, -100%, 0);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

.fadeInDown {
  animation-name: fadeInDown;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translate3d(0, 100%, 0);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

.fadeInUp {
  animation-name: fadeInUp;
}

/**
 * Vue Transitions
 */

.fade-enter-active,
.fade-leave-active {
  transition: opacity 150ms ease-out;
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
}
</style>
