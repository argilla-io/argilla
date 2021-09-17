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
