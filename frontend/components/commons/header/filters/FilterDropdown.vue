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
  <div
    ref="dropdownMenu"
    v-click-outside="onClickOutside"
    :class="[
      'dropdown',
      colorType === 'grey' ? '--grey' : '',
      visible ? 'dropdown--open' : '',
    ]"
  >
    <div class="dropdown__header" @click="onClick">
      <slot name="dropdown-header" />
    </div>
    <div v-show="visible" class="dropdown__content" :style="positionStyle">
      <slot name="dropdown-content" />
    </div>
  </div>
</template>
<script>
import ClickOutside from "v-click-outside";
export default {
  directives: {
    clickOutside: ClickOutside.directive,
  },
  data: () => {
    return {
      dropdownContentPosition: undefined,
      scrollContainerName: ".filters--scrollable",
      position: {},
    };
  },
  props: {
    visible: {
      default: false,
      type: Boolean,
    },
    colorType: {
      default: "white",
      type: String,
    },
  },
  computed: {
    positionStyle() {
      if (this.dropdownContentPosition) {
        return {
          top: `${this.dropdownContentPosition.top}px`,
          left: `${this.dropdownContentPosition.left}px`,
        };
      }
    },
    dropdownHeight() {
      return this.$refs.dropdownMenu.getBoundingClientRect().height;
    },
  },
  methods: {
    onClickOutside() {
      this.$emit("visibility", false);
    },
    getPosition() {
      if (document.querySelector(this.scrollContainerName)) {
        this.position = this.$refs.dropdownMenu.getBoundingClientRect();
        this.dropdownContentPosition = {
          top: this.position.top - this.dropdownHeight - 40,
          left: this.$refs.dropdownMenu.offsetLeft,
        };
      }
    },
    onClick() {
      this.$emit("visibility", !this.visible);
      if (document.querySelector(this.scrollContainerName)) {
        this.getPosition();
        document
          .querySelector(this.scrollContainerName)
          .addEventListener("scroll", this.handleScroll);
      }
    },
    handleScroll() {
      const scrollContainerHeight = document.querySelector(
        this.scrollContainerName
      ).offsetHeight;
      if (
        this.position.top - this.dropdownHeight - 20 > 0 &&
        this.position.top < scrollContainerHeight + this.dropdownHeight + 20
      ) {
        this.getPosition();
      } else {
        this.$emit("visibility", false);
      }
    },
  },
  beforeDestroy() {
    if (document.querySelector(this.scrollContainerName)) {
      document
        .querySelector(this.scrollContainerName)
        .removeEventListener("scroll", this.handleScroll);
    }
  },
};
</script>

<style lang="scss" scoped>
.dropdown {
  position: relative;
  &__header {
    height: 100%;
    width: auto;
    height: 45px;
    border: 1px solid palette(grey, 600);
    display: flex;
    align-items: center;
    padding: 0 20px;
    transition: all 0.2s ease;
    border-radius: $border-radius;
    &:after {
      content: "";
      border-color: $font-dark;
      border-style: solid;
      border-width: 1px 1px 0 0;
      display: inline-block;
      height: 8px;
      width: 8px;
      -webkit-transform: rotate(133deg);
      transform: rotate(133deg);
      -webkit-transition: all 1.5s ease;
      transition: all 1.5s ease;
      margin-bottom: 2px;
      margin-left: auto;
      margin-right: 0;
    }
    &:hover,
    &:focus {
      border-color: $primary-color;
      background: palette(white);
      transition: all 0.3s ease;
      &:after {
        border-color: $primary-color;
      }
    }
    // dropdown selected text
    > span {
      display: inline-block;
      max-width: 90%;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    p {
      display: inline-block;
      margin: 0;
      &:after {
        content: ",";
        position: relative;
        margin-right: 5px;
      }
      &:last-child {
        &:after {
          content: none;
        }
      }
    }
  }
  &__content {
    position: absolute;
    top: calc(100% + 10px);
    left: 0;
    margin-top: 0;
    box-shadow: $shadow;
    padding: 10px 20px 20px 20px;
    z-index: 3;
    transform: translate(0);
    right: auto;
    box-shadow: $shadow;
    border-radius: $border-radius;
    background: palette(white);
    .filter-options {
      border: none;
      outline: none;
      height: 40px;
      background: transparent;
    }
  }
  &--open {
    pointer-events: all;
    &.--grey {
      .dropdown__content,
      .dropdown__header {
        background: palette(grey, 700);
        border-color: palette(grey, 700);
      }
    }
    .dropdown__content {
      width: 270px;
    }
  }
}
</style>
