<template>
  <div class="radio-button" :class="[radioClasses]" @click.stop="toggleCheck">
    <div class="radio-button__container" :style="cssVars">
      <input
        type="radio"
        v-bind="{ id, name, disabled, value, checked: isSelected }"
      />
    </div>
    <label :for="id" class="radio-button__label" @click.prevent="toggleCheck">
      <slot />
    </label>
  </div>
</template>

<script>
import { isEqual } from "lodash";
export default {
  name: "BaseRadioButton",
  props: {
    id: {
      type: String,
    },
    name: {
      type: String,
    },
    model: {
      type: [String, Number, Boolean, Object],
    },
    value: {
      type: [String, Number, Boolean, Object],
    },
    disabled: Boolean,
    color: {
      type: String,
      default: "var(--fg-status-submitted)",
    },
  },
  model: {
    prop: "model",
    event: "change",
  },
  computed: {
    isSelected() {
      return isEqual(this.model, this.value);
    },
    radioClasses() {
      return {
        "--checked": this.isSelected,
        "--disabled": this.disabled,
      };
    },
    cssVars() {
      return {
        "--radio-color": this.color,
      };
    },
  },
  methods: {
    toggleCheck() {
      if (!this.disabled) {
        this.$emit("change", this.value);
      }
    },
  },
};
</script>

<style lang="scss">
$radio-button-size: 20px;

.radio-button {
  $this: &;
  position: relative;
  display: flex;
  margin: 16px 16px 16px 0;
  gap: $base-space;
  word-break: break-word;
  &:not(.--disabled) {
    cursor: pointer;
    #{$this}__label {
      cursor: pointer;
    }
  }
  &__container {
    width: $radio-button-size;
    min-width: $radio-button-size;
    height: $radio-button-size;
    position: relative;
    border: 1px solid var(--bg-opacity-20);
    background: var(--bg-accent-grey-2);
    border-radius: 50%;
    transition: all 0.2s ease;
    input {
      @extend %visuallyhidden;
    }
    &:before,
    &:after {
      content: " ";
      position: absolute;
      transition: all 0.2s ease;
    }
    &:before {
      width: $radio-button-size;
      height: $radio-button-size;
      top: 50%;
      left: 50%;
      z-index: 1;
      border-radius: 50%;
      transform: translate(-50%, -50%);
    }
    &:after {
      position: absolute;
      top: 6px;
      right: 6px;
      bottom: 6px;
      left: 6px;
      background: var(--bg-solid-grey-1);
      opacity: 0;
      border-radius: 50%;
      transform: scale3D(0, 0, 1);
    }
    &:hover {
      border-color: var(--radio-color);
      transition: border-color 0.3s ease-in-out;
    }
    &:focus {
      outline: none;
    }
  }

  &__label {
    position: relative;
    height: $radio-button-size;
    line-height: $radio-button-size;
  }
  &.--checked {
    #{$this}__container {
      background: var(--radio-color);
      border-color: var(--radio-color);
      &:after {
        opacity: 1;
        transform: scale3D(1, 1, 1);
        transition: all 0.3s ease;
      }
    }
  }
}
</style>
