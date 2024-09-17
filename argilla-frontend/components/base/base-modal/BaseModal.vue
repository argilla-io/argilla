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
  <transition v-if="modalVisible" name="modal" appear>
    <div class="modal-mask" :class="modalMaskClass">
      <div class="modal-wrapper" :class="modalPosition">
        <div
          class="modal-container"
          :class="modalClass"
          v-click-outside="closeModal"
        >
          <p v-if="modalTitle" class="modal__title">
            {{ modalTitle }}
          </p>
          <slot />
          <BaseButton
            class="button-close-modal"
            @on-click="closeModal"
            v-if="allowClose"
          >
            <svgicon name="close" width="20" height="20" />
          </BaseButton>
        </div>
      </div>
    </div>
  </transition>
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
    allowClose: {
      type: Boolean,
      default: false,
    },
    modalClass: {
      type: String,
      default: "modal-info",
    },
    modalIcon: {
      type: String,
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
  computed: {
    modalMaskClass() {
      return this.preventBodyScroll ? "prevent-scroll" : null;
    },
  },
  methods: {
    closeModal() {
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
  cursor: default;
  background: var(--bg-opacity-20);
  &:not(.prevent-scroll) {
    pointer-events: none;
  }
}

.modal-wrapper {
  display: flex;
  height: 100vh;
  &.modal-bottom-right {
    align-items: flex-end;
    padding-bottom: 3.5em;
    .modal-container {
      margin-right: 1.5em;
    }
  }
  &.modal-top-right {
    align-items: flex-start;
    padding-top: 10em;
    .modal-container {
      margin-right: 6em;
    }
  }

  &.modal-top-center {
    align-items: flex-start;
    padding-top: 5em;
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
  background-color: var(--bg-accent-grey-1);
  color: var(--fg-primary);
  border-radius: $border-radius;
  box-shadow: $shadow;
  transition: $swift-ease-in-out;
  text-align: left;
  pointer-events: all;
}
.button-close-modal {
  position: absolute;
  right: $base-space * 2;
  top: $base-space * 2;
  padding: 0;
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
  max-width: 440px;
  :deep(.modal__text) {
    margin-bottom: 2em;
  }
}

.modal-table {
  box-shadow: $shadow;
  border-radius: $border-radius;
  max-width: none;
  :deep(.modal__text) {
    margin-bottom: 2em;
  }
}

.modal-auto {
  box-shadow: $shadow;
  border-radius: $border-radius;
  max-width: none;
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

.modal-enter,
.modal-leave-active {
  opacity: 0;
}

.modal-enter .modal-container,
.modal-leave-active .modal-container {
  transform: scale(0.99);
}
</style>
