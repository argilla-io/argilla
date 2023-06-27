<template>
  <div class="container">
    <div class="inputs-area">
      <div class="input-button" v-for="option in options" :key="option.id">
        <input
          ref="options"
          type="checkbox"
          :name="option.text"
          :id="option.id"
          v-model="option.is_selected"
          @change="onSelect(option)"
          @focus="onFocus"
        />
        <label
          class="label-text cursor-pointer"
          :class="{ 'label-active': option.is_selected }"
          :for="option.id"
          v-text="option.text"
        />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "RatingMonoSelectionComponent",
  props: {
    options: {
      type: Array,
      required: true,
    },
    isFocused: {
      type: Boolean,
      default: () => false,
    },
  },
  model: {
    prop: "options",
    event: "on-change",
  },
  watch: {
    isFocused: {
      immediate: true,
      handler(newValue) {
        this.$nextTick(() => {
          !!newValue && this.$refs?.options[0].focus();
        });
      },
    },
  },
  methods: {
    onSelect({ id, is_selected }) {
      this.options.map((option) => {
        if (option.id === id) {
          option.is_selected = is_selected;
        } else {
          option.is_selected = false;
        }
        return option;
      });

      this.$emit("on-change", this.options);
    },
    onFocus() {
      this.$emit("on-focus");
    },
  },
};
</script>

<style lang="scss" scoped>
.container {
  display: flex;
  .inputs-area {
    display: inline-flex;
    gap: $base-space;
    border-radius: 5em;
    border: 1px solid #cdcdff;
    background: #e0e0ff;
    &:hover {
      border-color: darken(palette(purple, 800), 12%);
    }
  }
}
.label-text {
  display: flex;
  width: 100%;
  border-radius: 50em;
  height: 32px;
  background: palette(purple, 800);
  outline: none;
  padding-inline: 12px;
  line-height: 32px;
  font-weight: 500;
  overflow: hidden;
  color: palette(purple, 200);
  box-shadow: 0;
  transition: all 0.2s ease-in-out;
  &:not(.label-active):hover {
    background: darken(palette(purple, 800), 8%);
  }
}
input[type="checkbox"] {
  @extend %visuallyhidden;
  &:focus {
    & + .label-text {
      outline: 2px solid palette(purple, 200);
    }
  }
  // &:focus:not(:focus-visible) {
  //   & + .label-text {
  //     outline: none;
  //   }
  // }
}
.label-active {
  color: white;
  background: palette(purple, 200);
}
.cursor-pointer {
  cursor: pointer;
}
</style>
