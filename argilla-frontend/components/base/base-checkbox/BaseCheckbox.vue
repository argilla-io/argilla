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
  <div class="checkbox" :class="[classes]" @click.prevent="toggleCheck">
    <label v-if="$slots.default" :for="id" class="checkbox__label">
      <slot />
    </label>
    <div class="checkbox__container" tabindex="0">
      <input
        :id="id"
        type="checkbox"
        :disabled="disabled"
        :value="value"
        :checked="checked"
      />
      <svgicon color="#fffff" width="12" name="check" />
    </div>
  </div>
</template>

<script>
// TODO: Improve this component.
import "assets/icons/check";
import _ from "lodash";
export default {
  model: {
    prop: "areChecked",
    event: "change",
  },
  props: {
    id: {
      type: String,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    value: {
      type: [String, Number, Boolean, Object],
      default: false,
    },
    areChecked: {
      type: [Array, Boolean],
      default: false,
    },
    decorationCircle: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      checked: this.value || false,
    };
  },
  computed: {
    classes() {
      return {
        checked: Array.isArray(this.areChecked)
          ? Array.isArray(this.areChecked)
            ? this.areChecked.includes(this.value)
            : _.find(this.areChecked, this.value)
          : this.checked,
        disabled: this.disabled,
        "decoration-circle": this.decorationCircle,
      };
    },
  },
  watch: {
    value() {
      this.checked = !!this.value;
    },
    areChecked(newValue) {
      if (typeof newValue === "boolean") {
        this.checked = newValue;
      }
    },
  },
  methods: {
    toggleCheck() {
      if (!this.disabled) {
        if (Array.isArray(this.areChecked)) {
          const checked = this.areChecked.slice();
          const found =
            typeof this.value === "string"
              ? checked.indexOf(this.value)
              : _.findIndex(checked, this.value);
          if (found !== -1) {
            checked.splice(found, 1);
          } else {
            checked.push(this.value);
          }
          this.$emit("change", checked);
        } else {
          this.checked = !this.checked;
          let checked = this.areChecked;
          checked = this.checked;
          this.$emit("change", checked);
          this.$emit("input", checked);
        }
      }
    },
  },
};
</script>
<style lang="scss" scoped>
$checkbox-size: 16px;
$checkbox-touch-size: 16px;
$checkbox-color: var(--bg-solid-grey-3);
$checkbox-color-dark: var(--bg-action);
$checkbox-border-radius: 3px;
$checkbox-decoration-circle-color: #6b87f8;
.checkbox {
  width: auto;
  display: inline-flex;
  position: relative;
  &.disabled {
    opacity: 0.6;
  }
  &:not(.disabled) {
    cursor: pointer;
    .checkbox-label {
      cursor: pointer;
    }
  }
  &__container {
    width: $checkbox-size;
    min-width: $checkbox-size;
    height: $checkbox-size;
    position: relative;
    border-radius: $checkbox-border-radius;
    border: 1px solid $checkbox-color;
    text-align: center;
    vertical-align: middle;
    margin-right: 0;
    margin-left: auto;
    .svg-icon {
      fill: var(--color-white);
      transform: scale(0);
      transition: all 0.2s ease-in-out;
      display: block;
      margin: auto;
    }
    &:focus {
      outline: none;
    }
    input {
      position: absolute;
      left: -999em;
    }
  }
  &__label {
    line-height: $checkbox-size;
    margin-right: $base-space;
    word-break: break-word;
    hyphens: auto;
  }
  &--dark {
    .checkbox__container {
      border: 1px solid var(--bg-opacity-20);
      &:after {
        background: $checkbox-color-dark;
      }
    }
  }
  &.decoration-circle {
    .checkbox__container {
      animation: checkbox-animation 1s forwards;
      &:after,
      &:before {
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        border-radius: $border-radius-rounded;
        transition: transition 0.3s ease-in-out;
      }
      &:after {
        animation: checkbox-animation-circle 1s forwards;
        transition: all 0.3s ease-in-out;
      }
    }
    &:hover {
      .checkbox__container {
        &:before {
          transform: scale(2.2);
          background: $checkbox-decoration-circle-color;
          opacity: 0.1;
          transition: transform 0.3s ease-in-out;
        }
      }
    }
  }
}

.checkbox.checked {
  .checkbox__container {
    background: var(--bg-action);
    border: 1px solid var(--bg-action);
    .svg-icon {
      transform: scale(1);
      transition: all 0.2s ease-in-out;
    }
  }
}

@keyframes checkbox-animation {
  0% {
    transform: scale(0);
    border-radius: 50%;
    background: white;
  }
  50% {
    background: white;
  }
  100% {
    transform: scale(1);
    border-radius: $checkbox-border-radius;
  }
}
@keyframes checkbox-animation-circle {
  0% {
    transform: scale(0);
    background: $checkbox-decoration-circle-color;
    opacity: 1;
  }
  70% {
    transform: scale(2.2);
    opacity: 1;
  }
  100% {
    transform: scale(0);
    opacity: 0;
  }
}
</style>
