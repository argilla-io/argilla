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
  <div class="re-checkbox" :class="[classes]">
    <label
      v-if="$slots.default"
      :for="id"
      class="checkbox-label"
      @click.prevent="toggleCheck"
    >
      <slot />
    </label>
    <div class="checkbox-container" tabindex="0" @click="toggleCheck">
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
import "assets/icons/check";
import _ from "lodash";
export default {
  model: {
    prop: "areChecked",
    event: "change",
  },
  props: ["areChecked", "value", "id", "disabled"],
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
$checkbox-size: 20px;
$checkbox-touch-size: 20px;
$checkbox-color: palette(grey, 600);
$checkbox-color-dark: $primary-color;
.re-checkbox {
  width: auto;
  margin: 16px 8px 16px 0;
  display: inline-flex;
  position: relative;
  border-radius: 1px;
  &.disabled {
    opacity: 0.6;
  }
  &:not(.disabled) {
    cursor: pointer;
    .checkbox-label {
      cursor: pointer;
    }
  }
  .checkbox-container {
    width: $checkbox-size;
    min-width: $checkbox-size;
    height: $checkbox-size;
    position: relative;
    border-radius: 1px;
    border: 1px solid $checkbox-color;
    text-align: center;
    vertical-align: middle;
    text-align: center;
    margin-right: 0;
    margin-left: auto;
    .svg-icon {
      fill: palette(white);
      transform: scale(0);
      transition: all 0.2s ease-in-out;
      display: block;
      margin: auto;
      margin-top: 2px;
    }
    &:focus {
      outline: none;
    }
    input {
      position: absolute;
      left: -999em;
    }
  }
  .checkbox-label {
    line-height: $checkbox-size;
    margin-right: 0.5em;
    word-break: break-word;
    hyphens: auto;
  }
  &--dark {
    &.checked {
      .checkbox-label {
        color: $primary-color;
      }
    }
    .checkbox-container {
      border: 1px solid $primary-color;
      &:after {
        background: $checkbox-color-dark;
      }
    }
  }
}

.checkbox-label {
  .dropdown--filter & {
    height: auto;
    white-space: normal;
    text-transform: none;
    word-break: break-word;
    hyphens: auto;
  }
}

.re-checkbox.checked {
  .checkbox-container {
    background: $primary-color;
    border: 1px solid $primary-color;
    .svg-icon {
      transform: scale(1);
      transition: all 0.2s ease-in-out;
    }
  }
}
</style>
