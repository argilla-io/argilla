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
          <p v-if="modalTitle" class="modal__title">
            <svgicon
              v-if="modalIcon"
              width="24"
              height="24"
              :name="modalIcon"
              color="#000000"
            ></svgicon>
            {{ modalTitle }}
          </p>
          <slot />
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import "assets/icons/close";
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
    modalClass: {
      type: String,
      default: "modal-info",
    },
    modalIcon: {
      type: String,
      default: undefined,
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
      default: "modal-center",
    },
  },
  data: () => ({}),
  watch: {
    modalVisible() {
      if (this.preventBodyScroll) {
        if (this.modalVisible) {
          document.body.classList.add("--fixed");
        } else {
          document.body.classList.remove("--fixed");
        }
      }
    },
  },
  beforeDestroy() {
    if (this.preventBodyScroll) {
      document.body.classList.remove("--fixed");
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
  background: $black-4;
}

.modal-wrapper {
  display: flex;
  height: 100vh;
  &.modal-bottom-right {
    align-items: flex-end;
    padding-bottom: 6em;
    .modal-container {
      margin-right: 6em;
    }
  }
  &.modal-top-right {
    align-items: flex-start;
    padding-bottom: 6em;
    .modal-container {
      margin-right: 6em;
    }
  }
  &.modal-center {
    align-items: center;
  }
}

.modal-container {
  position: relative;
  max-width: 460px;
  margin: 0px auto;
  padding: $base-space * 4;
  background-color: palette(white);
  color: $black-87;
  border-radius: $border-radius;
  box-shadow: $shadow;
  transition: $swift-ease-in-out;
  text-align: left;
  pointer-events: all;
}
.modal-primary {
  box-shadow: $shadow;
  border-radius: $border-radius;
  max-width: 520px;
  :deep(.modal__text) {
    margin-bottom: 2em;
  }
}
.modal-secondary {
  box-shadow: $shadow;
  border-radius: $border-radius;
  max-width: 400px;
  :deep(.modal__text) {
    margin-bottom: 2em;
  }
}

:deep(.modal-buttons) {
  display: flex;
  .button {
    width: 100%;
    justify-content: center;
    &:last-child {
      margin-left: $base-space * 2;
    }
  }
}
:deep(.modal__title) {
  display: flex;
  align-items: center;
  gap: $base-space;
  @include font-size(16px);
  font-weight: 600;
  margin-top: 0;
}

.modal-enter {
  opacity: 0;
}

.modal-leave-active {
  opacity: 0;
}

.modal-enter .modal-container,
.modal-leave-active .modal-container {
  transform: scale(0.9);
}
</style>
