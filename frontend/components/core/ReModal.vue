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
  <div v-if="modalVisible" v-click-outside="onClickOutside" class="modal-mask">
    <transition name="fade" appear>
      <div class="modal-wrapper" :class="modalPosition">
        <div :class="['modal-container', modalClass]">
          <p v-if="!modalCustom" class="modal__title">
            <span
              class="state"
              :class="modalClass === 'modal-info' ? 'succeeded' : 'failed'"
            />
            {{ modalTitle }}
          </p>
          <div v-if="!modalCustom" />
          <slot />
          <ReButton
            v-if="modalCloseButton"
            class="modal-close"
            @click="$emit('close-modal')"
          >
            <span class="modal-close__text">close</span>
            <svgicon name="cross" width="10" height="auto" />
          </ReButton>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import "assets/icons/cross";
import ClickOutside from "v-click-outside";
export default {
  directives: {
    clickOutside: ClickOutside.directive,
  },
  props: {
    modalCloseButton: {
      type: Boolean,
      default: true,
    },
    modalVisible: {
      type: Boolean,
      default: true,
    },
    modalCustom: {
      type: Boolean,
      default: false,
    },
    modalClass: {
      type: String,
      default: "modal-info",
    },
    modalTitle: {
      type: String,
      default: undefined,
    },
    preventBodyScroll: {
      type: Boolean,
      default: false,
    },
    messages: {
      type: Array,
      default: () => [],
    },
    modalPosition: {
      type: String,
      default: "modal-bottom",
    },
  },
  data: () => ({}),
  updated() {
    if (this.preventBodyScroll) {
      if (this.modalVisible) {
        document.body.classList.add("--fixed");
      } else {
        document.body.classList.remove("--fixed");
      }
    }
  },
  methods: {
    onClickOutside() {
      this.$emit("close-modal");
    },
  },
};
</script>

<style lang="scss" scoped>
.modal-mask {
  position: fixed;
  z-index: 9998;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  display: table;
  transition: opacity 0.3s ease;
  pointer-events: none;
  cursor: default;
  background: rgba(0, 0, 0, 0.1);
}

.modal-wrapper {
  display: table-cell;
  vertical-align: middle;
  &.modal-bottom {
    vertical-align: bottom;
    padding-bottom: 3em;
    padding-left: 30%;
  }
  &.modal-center {
    vertical-align: middle;
  }
}

.modal-container {
  max-width: 460px;
  margin: 0px auto;
  padding: 1.5em;
  background-color: $lighter-color;
  border-radius: 4px;
  box-shadow: 0px 2px 4px 3px rgba(0, 0, 0, 0.27);
  transition: $swift-ease-in-out;
  position: relative;
  text-align: left;
  pointer-events: all;
}
.modal-primary {
  box-shadow: 0 5px 11px 0 rgba(0, 0, 0, 0.5);
  border-radius: 0;
  max-width: 520px;
  ::v-deep .modal__title {
    font-weight: normal;
    @include font-size(16px);
  }
  ::v-deep .modal__text {
    margin-bottom: 2em;
  }
  .modal-close {
    color: $primary-color;
    font-weight: 600;
    &__text {
      margin-right: 10px;
    }
  }
}
.modal-secondary {
  border: 1px solid $secondary-color;
  border-radius: 0;
  box-shadow: none;
  max-width: 400px;
  ::v-deep .modal__title {
    color: $secondary-color;
  }
  ::v-deep .modal__text {
    margin-bottom: 2em;
  }
  .modal-close {
    color: $secondary-color;
    font-weight: 600;
    &__text {
      margin-right: 10px;
    }
  }
}

::v-deep .modal-buttons {
  text-align: right;
}
::v-deep .modal__title {
  @include font-size(14px);
  color: $font-dark-color;
  font-weight: 600;
  margin-top: 0;
  margin-right: 2em;
}

.modal__message {
  margin-bottom: 1em;
  display: block;
  &:last-of-type {
    margin-bottom: 0;
  }
  .modal-text {
    margin-top: 0;
    margin-bottom: 0.3em;
    font-weight: 600;
    &--info {
      margin-top: 0;
      margin-bottom: 0.3em;
      display: block;
      font-weight: lighter;
    }
  }
  .failed {
    color: $error;
    font-weight: lighter;
    margin-bottom: 0;
    margin-top: 0;
  }
}

.modal-enter {
  opacity: 0;
}

.modal-leave-active {
  opacity: 0;
}

.modal-buttons {
  text-align: right;
}

.modal-close {
  border: 0;
  background: $lighter-color;
  color: $font-medium-color;
  position: absolute;
  top: 0.5em;
  right: 0.5em;
  outline: none;
  cursor: pointer;
}

.modal-enter .modal-container,
.modal-leave-active .modal-container {
  transform: scale(0.9);
}
</style>
