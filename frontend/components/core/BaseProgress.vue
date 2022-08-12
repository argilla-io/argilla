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
  <transition name="re-progress" :duration="2500" appear>
    <div class="re-progress__container">
      <p v-if="tooltip" class="re-progress__tooltip" :style="tooltipStyles">
        <span class="triangle" :style="tooltipTriangleStyles"></span
        >{{ tooltip }}
      </p>
      <div class="re-progress" :style="backgroundStyles">
        <div class="re-progress-track" :style="styles"></div>
        <div
          v-if="multiple"
          class="re-progress-track--secondary"
          :style="stylesSecondary"
        />
      </div>
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
    color: {
      type: String,
    },
    tooltip: {
      default: undefined,
      type: String,
    },
  },
  computed: {
    styles() {
      return {
        width: `${this.progress}%`,
        backgroundColor: this.color,
      };
    },
    backgroundStyles() {
      return {
        backgroundColor: this.color,
      };
    },
    tooltipStyles() {
      return {
        left: this.progress > 80 ? `80%` : `${this.progress}%`,
        backgroundColor: this.color,
      };
    },
    tooltipTriangleStyles() {
      return {
        borderRightColor: this.color,
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
  height: 22px;
  position: relative;
  overflow: hidden;
  background: #a1a2cc;
  border-top-left-radius: 0;
  border-top-right-radius: 10px;
  border-top-left-radius: 0;
  border-bottom-right-radius: 10px;
  margin: 0 0 1.5em 0;
  &:before {
    content: "";
    position: absolute;
    background: white;
    opacity: 0.7;
    top: 0;
    bottom: 0;
    right: 0;
    left: 0;
  }
  &__container {
    position: relative;
    &:hover {
      .re-progress__tooltip {
        clip-path: none;
        opacity: 1;
        transition: opacity 0.5s linear 0.3s;
      }
    }
  }
  &__tooltip {
    padding: 0.5em 1em;
    top: -5px;
    transform: none;
    background: palette(blue, 200);
    color: white;
    border: none;
    border-radius: 3px;
    @include font-size(14px);
    font-weight: 600;
    position: absolute;
    margin: 0 0 0 6px;
    z-index: 1;
    clip-path: circle(0);
    opacity: 0;
    transition: opacity 0.5s linear 0.3s;
    border-color: lime !important;
    .triangle {
      @include triangle(left, 6px, 6px, palette(blue, 200));
      position: absolute;
      left: -6px;
      top: calc(50% - 6px);
    }
  }
  &--minimal {
    @extend .re-progress;
    height: 2px;
    .re-progress-track {
      background: palette(grey, 300);
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
  border-bottom-left-radius: 2px;
  border-top-left-radius: 2px;
  background: palette(blue, 200);
  transition: width 1s linear, left 1s linear;
  &:last-of-type {
    border-bottom-left-radius: 0;
    border-top-left-radius: 0;
  }
  .re-progress-enter-active & {
    animation: progress 1s 0.5s;
    transform-origin: 0 50%;
    animation-fill-mode: backwards;
  }
  &--secondary {
    @extend .re-progress-track;
    left: auto;
    right: 0;
    background: #a1a2cc;
    transition: width 1s linear, left 1s linear;
    .re-progress-enter-active & {
      animation: progress 1s 1.5s;
      animation-fill-mode: backwards;
    }
  }
}
@keyframes progress {
  0% {
    transform: scaleX(0);
  }
  100% {
    transform: scaleX(1);
  }
}
</style>
