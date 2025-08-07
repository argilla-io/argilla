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
    :class="{ disabled: !checked, 'disable-action': disableAction }"
    class="switch"
  >
    <label v-if="$slots.default" :for="id || name" class="switch-label">
      <slot />
    </label>
    <div
      class="switch-container"
      type="button"
      role="switch"
      @click="toggle($event)"
      :aria-label="`${name} ${checked ? 'on' : 'off'}`"
      :aria-checked="checked ? 'true' : 'false'"
    >
      <div class="switch-thumb" :style="styles">
        <input
          :id="id || name"
          type="checkbox"
          :name="name"
          :disabled="disabled"
          :value="value"
          tabindex="-1"
        />
        <div class="switch-holder">
          <svgicon
            width="10"
            height="10"
            name="check"
            color="white"
            aria-hidden="true"
          ></svgicon>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
const checkedPosition = 70;
const initialPosition = "-1px";

import "assets/icons/check";
export default {
  props: {
    name: String,
    value: Boolean,
    id: String,
    disabled: Boolean,
    disableAction: {
      type: Boolean,
      default: false,
    },
    type: {
      type: String,
      default: "button",
    },
  },
  data() {
    return {
      leftPos: initialPosition,
      checked: Boolean(this.value),
    };
  },
  computed: {
    classes() {
      return {
        "re-checked": this.checked,
        "re-disabled": this.disabled,
      };
    },
    styles() {
      return {
        transform: `translate3D(${this.leftPos}, -50%, 0)`,
      };
    },
  },
  watch: {
    checked() {
      this.setPosition();
    },
    value(value) {
      this.changeState(value);
    },
  },
  mounted() {
    this.$nextTick(this.setPosition);
  },
  methods: {
    setPosition() {
      this.leftPos = this.checked ? `${checkedPosition}%` : initialPosition;
    },
    changeState(checked, $event) {
      if (typeof $event !== "undefined") {
        this.$emit("change", checked, $event);

        if (!$event.defaultPrevented) {
          this.checked = checked;
        }
        this.$emit("input", this.checked, $event);
      } else {
        this.checked = checked;
      }
    },
    toggle($event) {
      if (!this.disabled && !this.disableAction) {
        this.changeState(!this.checked, $event);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
$switch-width: 28px;
$switch-height: 11px;
$switch-thumb-size: 18px;
.switch {
  display: flex;
  align-items: center;
  position: relative;
  &.disabled {
    svg {
      display: none;
    }
    .switch-thumb {
      background-color: #f0f0f0 !important;
    }
  }
  &.disable-action {
    opacity: 0.5;
    pointer-events: none;
    cursor: default;
    .switch-thumb {
      background-color: var(--color-white) !important;
      transform: translate3d(-1px, -50%, 0px) !important;
    }
    &:active {
      .switch-thumb {
        transform: translate3d(50%, -50%, 0px) !important;
      }
    }
  }
  .switch-container {
    width: $switch-width;
    height: $switch-height;
    position: relative;
    border-radius: $switch-height;
    transition: $swift-ease-out;
    background-color: var(--bg-opacity-20);
    cursor: pointer;
    .switch-thumb {
      width: $switch-thumb-size;
      height: $switch-thumb-size;
      position: absolute;
      top: 50%;
      left: 0;
      background-color: var(--bg-action);
      border-radius: 50%;
      transition: $swift-linear;
    }
    input {
      position: absolute;
      left: -999em;
    }
    .switch-holder {
      @include absoluteCenter;
      width: $switch-thumb-size;
      height: $switch-thumb-size;
      display: flex;
      justify-content: center;
      align-items: center;
      margin: 0;
      padding: 0;
      z-index: 2;
      background: none;
      border: none;
      cursor: pointer;
      &:focus {
        outline: none;
      }
    }
  }
  .switch-label {
    margin-right: 1em;
    color: var(--fg-primary);
  }
}
</style>
