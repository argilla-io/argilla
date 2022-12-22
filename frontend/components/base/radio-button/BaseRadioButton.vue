<template>
  <div class="radio-button" :class="[radioClasses]">
    <div class="radio-button__container" @click.stop="toggleCheck">
      <input
        type="radio"
        v-bind="{ id, name, disabled, value, checked: isSelected }"
      />
    </div>
    <label :for="id" class="radio-button-label" @click.prevent="toggleCheck">
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
  width: auto;
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
    border: 1px solid palette(grey, 600);
    border-radius: 50%;
    transition: all 0.2s ease;
    input {
      position: absolute;
      left: -999em;
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
      background: palette(white);
      opacity: 0;
      border-radius: 50%;
      transform: scale3D(0, 0, 1);
    }
    &:focus {
      outline: none;
    }
  }

  &__label {
    position: relative;
    height: $radio-button-size;
    padding-left: 16px;
    line-height: $radio-button-size;
  }
  &.--checked {
    #{$this}__container {
      background: $primary-color;
      border-color: $primary-color;
      &:after {
        opacity: 1;
        transform: scale3D(1, 1, 1);
        transition: all 0.2s ease;
      }
    }
  }
}
</style>
