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
    <div class="checkbox-container" tabindex="0" @click.stop="toggleCheck">
      <input
        :id="id"
        type="checkbox"
        :disabled="disabled"
        :value="value"
        :checked="checked"
      />
    </div>
  </div>
</template>

<script>
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
          ? this.areChecked.includes(this.value)
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
    toggleCheck($event) {
      if (!this.disabled) {
        if (Array.isArray(this.areChecked)) {
          const checked = this.areChecked.slice();
          const found = checked.indexOf(this.value);
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
$checkbox-color: $line-smooth-color;
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
  &.--custom {
    display: block;
    @extend %clearfix;
    margin-right: 0;
    input {
      display: none;
      &:checked + label {
        &:after {
          opacity: 1;
          transform: scale3D(1, 1, 1);
          transition: $swift-ease-out;
        }
      }
    }
    label {
      position: relative;
      display: block;
      margin-left: 25px;
      &:before {
        top: 2px;
        border-radius: 1px;
        border: 1px solid $darker-color;
        transition: $swift-ease-out;
        width: 15px;
        height: 15px;
        position: absolute;
        left: -25px;
        transition: $swift-ease-in;
        content: " ";
      }
      &:after {
        opacity: 0;
        width: 11px;
        height: 11px;
        background: $darker-color;
        position: absolute;
        left: -23px;
        top: 4px;
        transform: scale3D(0.15, 0.15, 1);
        transition: $swift-ease-in;
        content: "";
      }
    }
  }
  .checkbox-container {
    width: $checkbox-size;
    min-width: $checkbox-size;
    height: $checkbox-size;
    position: relative;
    border-radius: 1px;
    border: 1px solid $checkbox-color;
    background: $lighter-color;
    transition: $swift-ease-out;
    &:focus {
      outline: none;
    }
    &:after {
      border-radius: 1px;
      opacity: 0;
      width: 16px;
      height: 16px;
      background: $primary-color;
      position: absolute;
      left: 1px;
      top: 1px;
      transform: scale3D(0.15, 0.15, 1);
      transition: $swift-ease-in;
      content: "";
    }
    input {
      position: absolute;
      left: -999em;
    }
  }
  .checkbox-label {
    height: $checkbox-size;
    line-height: $checkbox-size;
    margin-right: auto;
  }
  &--dark {
    &.checked {
      .checkbox-label {
        color: $primary-color;
      }
    }
    .checkbox-container {
      border: 1px solid palette(grey);
      &:after {
        background: $checkbox-color-dark;
      }
    }
  }
}

.checkbox-label {
  .dropdown--filter & {
    height: auto;
    padding-right: 2em;
    white-space: nowrap;
    text-transform: none;
  }
}

.re-checkbox.checked {
  .checkbox-container {
    &:after {
      opacity: 1;
      transform: scale3D(1, 1, 1);
      transition: $swift-ease-out;
    }
  }
}
</style>
