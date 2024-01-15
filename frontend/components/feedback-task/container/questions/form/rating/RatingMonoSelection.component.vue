<template>
  <div class="container">
    <div class="inputs-area">
      <div
        class="input-button"
        v-for="option in options"
        :key="option.id"
        @keydown.enter.prevent
        :data-title="
          suggestions === option.value
            ? $t('suggestion.name')
            : option.isSelected
            ? $t('annotation')
            : null
        "
      >
        <input
          ref="options"
          type="checkbox"
          :name="option.value"
          :id="option.id"
          v-model="option.isSelected"
          @change="onSelect(option)"
          @focus="onFocus"
        />
        <label
          class="label-text"
          :class="{
            'label-active': option.isSelected,
            '--suggestion': suggestions === option.value,
          }"
          :for="option.id"
          v-text="option.value"
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
    suggestions: {
      type: Number,
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
        if (newValue) {
          this.$nextTick(() => {
            const options = this.$refs?.options;
            if (options.some((o) => o.contains(document.activeElement))) {
              return;
            }
            options[0].focus();
          });
        }
      },
    },
  },
  methods: {
    onSelect({ id, isSelected }) {
      this.options.forEach((option) => {
        option.isSelected = option.id === id ? isSelected : false;
      });

      this.$emit("on-change", this.options);

      if (isSelected) {
        this.$emit("on-selected");
      }
    },
    onFocus() {
      this.$emit("on-focus");
    },
  },
};
</script>

<style lang="scss" scoped>
$suggestion-color: palette(yellow, 400);
.container {
  display: flex;
  .inputs-area {
    display: inline-flex;
    gap: $base-space;
    border-radius: $border-radius-rounded;
    border: 1px solid #cdcdff;
    background: #e0e0ff;
    &:hover {
      border-color: darken(palette(purple, 800), 12%);
    }
  }
}
.label-text {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  border-radius: $border-radius-rounded;
  height: $base-space * 4;
  min-width: $base-space * 4;
  padding-inline: $base-space;
  outline: none;
  background: palette(purple, 800);
  color: palette(purple, 200);
  font-weight: 500;
  overflow: hidden;
  transition: all 0.2s ease-in-out;
  cursor: pointer;
  &.--suggestion {
    background: $suggestion-color;
    &:not(.label-active):hover {
      background: darken($suggestion-color, 8%);
    }
  }
  &.label-active {
    color: white;
    background: palette(purple, 200);
    &.--suggestion {
      border: 2px solid $suggestion-color;
    }
  }

  &:not(.label-active):hover {
    background: darken(palette(purple, 800), 8%);
  }
}
input[type="checkbox"] {
  @extend %visuallyhidden;
  &:focus {
    & + .label-text {
      outline: 2px solid $primary-color;
    }
  }
}
.input-button:not(:first-of-type) {
  input[type="checkbox"] {
    &:focus:not(:focus-visible) {
      & + .label-text {
        outline: none;
        &.label-active {
          outline: none;
        }
      }
    }
  }
}

[data-title] {
  position: relative;
  overflow: visible;
  @include tooltip-mini("top");
}
</style>
