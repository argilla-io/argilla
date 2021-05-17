<template>
  <div class="re-annotation-button" :class="classes">
    <label :for="id" class="button" @click.prevent="toggleCheck">
      <span class="annotation-button-data__text" :title="label.class"
        >{{ label.class }}
      </span>
      <div class="annotation-button-data__info">
        <ReNumeric
          v-if="decorateConfidence(label.confidence)"
          class="annotation-button-data__confidence"
          :value="decorateConfidence(label.confidence)"
          type="%"
          :decimals="0"
        ></ReNumeric>
      </div>
    </label>
    <div
      class="annotation-button-container"
      tabindex="0"
      @click.stop="toggleCheck"
    >
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
  props: ["areChecked", "value", "id", "disabled", "label", "allowMultiple"],
  data() {
    return {
      checked: this.value || false,
    };
  },
  computed: {
    classes() {
      return {
        active: Array.isArray(this.areChecked)
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
  },
  methods: {
    decorateConfidence(confidence) {
      return confidence * 100;
    },
    toggleCheck() {
      if (!this.disabled) {
        let checked = this.areChecked.slice();
        const found = checked.indexOf(this.value);
        if (found >= 0) {
          checked.splice(found, 1);
        } else {
          if (checked.length && !this.allowMultiple) {
            checked = [];
          }
          checked.push(this.value);
        }
        this.$emit("change", checked);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
$annotation-button-size: 20px;
$annotation-button-touch-size: 48px;
.re-annotation-button {
  width: auto;
  margin: 16px 8px 16px 0;
  display: inline-flex;
  position: relative;
  .annotation-button-container {
    display: none;
  }
  &.label-button {
    margin: auto auto 20px auto;
    color: $darker-color;
    padding: 0;
    transition: all 0.3s ease;
    max-width: 238px;
    width: 100%;
    border-radius: 7px;
    .button {
      outline: none;
      cursor: pointer;
      border-radius: 5px;
      background: $lighter-color;
      border: 1px solid $line-smooth-color;
      height: 40px;
      line-height: 40px;
      padding-left: 0.5em;
      padding-right: 0.5em;
      width: 100%;
      display: flex;
      font-weight: 600;
      overflow: hidden;
      color: $darker-color;
    }
    &.active {
      .button {
        background: $secondary-color;
        border: 1px solid $secondary-color;
      }
      transition: all 0.02s ease-in-out;
      box-shadow: none; // Animate the size, outside
      animation: pulse 0.4s;
      transform: scale3d(1, 1, 1);
      -webkit-font-smoothing: antialiased;
      transform: translate3d(1, 1, 1); // z-index: 1;
      &:after {
        display: none !important;
      }
      @keyframes pulse {
        0% {
          transform: scale3d(1, 1, 1);
        }
        70% {
          transform: scale3d(1.04, 1.04, 1.04);
        }
        100% {
          transform: scale3d(1, 1, 1);
        }
      }
      @keyframes pulse-font {
        0% {
          transform: scale3d(1, 1, 1);
        }
        70% {
          transform: scale3d(1.06, 1.06, 1.06);
        }
        100% {
          transform: scale3d(1, 1, 1);
        }
      }
      .annotation-button-data__text,
      .annotation-button-data__confidence {
        color: $lighter-color;
        animation: pulse-font 0.5s;
      }
    }
    .annotation-button-data {
      overflow: hidden;
      transition: transform 0.3s ease;
      &__text {
        max-width: calc(100% - 10px);
        overflow: hidden;
        text-overflow: ellipsis;
        display: inline-block;
        white-space: nowrap;
        vertical-align: top;
      }
      &__info {
        margin-right: 0;
        margin-left: auto;
        transform: translateY(0);
        transition: all 0.3s ease;
      }
      &__confidence {
        width: 40px;
        @include font-size(12px);
        display: inline-block;
        text-align: center;
        line-height: 1.5em;
        border-radius: 2px;
      }
    }
    &:not(.active):hover {
      box-shadow: 0px 3px 8px 3px rgba(222, 222, 222, 0.4) !important;
      border-color: $line-light-color;
    }
  }
  &.disabled {
    opacity: 0.5;
  }
  &:not(.disabled) {
    cursor: pointer;
    .annotation-button {
      cursor: pointer;
    }
  }
  .annotation-button {
    height: $annotation-button-size;
    padding-left: 8px;
    line-height: $annotation-button-size;
  }
}

// .re-annotation-button.checked {
//   .annotation-button-container {
//     &:after {
//       opacity: 1;
//       transform: scale3D(1, 1, 1);
//       transition: $swift-ease-out;
//     }
//   }
// }
</style>
