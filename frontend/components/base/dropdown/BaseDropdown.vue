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
  <div v-click-outside="onClickOutside" class="dropdown">
    <div class="dropdown__header" @click="onClick">
      <slot name="dropdown-header" />
    </div>
    <transition appear name="fade">
      <div v-show="visible" class="dropdown__content">
        <slot name="dropdown-content" />
      </div>
    </transition>
  </div>
</template>
<script>
import ClickOutside from "v-click-outside";
export default {
  directives: {
    clickOutside: ClickOutside.directive,
  },
  props: {
    visible: {
      default: false,
      type: Boolean,
    },
  },
  methods: {
    onClickOutside() {
      this.$emit("visibility", false);
    },
    onClick() {
      this.$emit("visibility", !this.visible);
    },
  },
};
</script>

<style lang="scss" scoped>
.dropdown {
  position: relative;
  color: $black-54;
  &__header {
    display: flex;
    align-items: center;
    transition: all 0.2s ease;
    border-radius: $border-radius;
    &:hover,
    &:focus {
      border-color: $black-37;
      background: palette(white);
      transition: all 0.3s ease;
      &:after {
        border-color: $black-54;
      }
    }
  }
  &__content {
    position: absolute;
    top: calc(100% + 10px);
    right: 0;
    width: 270px;
    margin-top: 0;
    padding: $base-space * 3;
    z-index: 3;
    transform: translate(0);
    box-shadow: $shadow;
    border-radius: $border-radius;
    background: palette(white);
  }
}
</style>
