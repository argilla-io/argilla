<template>
  <div
    :class="{ disabled: !checked, 'disable-action': disableAction }"
    class="re-switch"
  >
    <label v-if="$slots.default" :for="id || name" class="re-switch-label">
      <slot />
    </label>
    <div class="re-switch-container" @click="toggle($event)">
      <div class="re-switch-thumb" :style="styles">
        <input
          :id="id"
          type="checkbox"
          :name="name"
          :disabled="disabled"
          :value="value"
          tabindex="-1"
        />
        <button :type="type" class="re-switch-holder">
          <svgicon
            width="12"
            height="12"
            name="check"
            color="white"
          ></svgicon>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
const checkedPosition = 90;
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
$switch-width: 44px;
$switch-height: 13px;
$switch-thumb-size: 24px;
$switch-ripple-size: 48px;
.re-switch {
  width: auto;
  margin: 0;
  display: inline-flex;
  position: relative;
  &.disabled {
    svg {
      display: none;
    }
    .re-switch-thumb {
      background-color: $lighter-color !important;
    }
  }
  &.disable-action {
    opacity: 0.5;
    .re-switch-thumb {
      background-color: $lighter-color !important;
      transform: translate3d(-1px, -50%, 0px) !important;
    }
    &:active {
      .re-switch-thumb {
        transform: translate3d(90%, -50%, 0px) !important;
      }
    }
  }
  .re-switch-container {
    width: $switch-width;
    height: $switch-height;
    position: relative;
    border-radius: $switch-height;
    transition: $swift-ease-out;
    background-color: palette(grey, smooth);
    .re-switch-thumb {
      box-shadow: $shadow;
      width: $switch-thumb-size;
      height: $switch-thumb-size;
      position: absolute;
      top: 50%;
      left: 0;
      background-color: $primary-color;
      border-radius: 50%;
      transition: $swift-linear;
    }
    input {
      position: absolute;
      left: -999em;
    }
    .re-switch-holder {
      @include absoluteCenter;
      width: 40px;
      height: 40px;
      margin: 0;
      padding: 0;
      z-index: 2;
      background: none;
      border: none;
      &:focus {
        outline: none;
      }
    }
  }
  .re-switch-label {
    height: $switch-height;
    line-height: $switch-height;
    margin-right: 1em;
  }
}

.re-switch.re-dragging {
  .re-switch-thumb {
    cursor: grabbing;
  }
}

.re-switch.re-disabled {
  .re-switch-thumb {
    cursor: default;
  }
}
</style>
