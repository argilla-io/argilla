<template>
  <div class="container">
    <div class="inputs-area">
      <div
        class="input-button"
        v-for="option in options"
        :key="option.id"
        @keydown.enter.prevent
      >
        <BaseTooltip
          :text="getSuggestion(option) ? getTooltipText(option) : null"
          minimalist
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
            }"
            :for="option.id"
          >
            {{ option.value }}

            <svgicon
              v-if="getSuggestion(option)"
              class="label-text__suggestion-icon"
              name="suggestion"
            />
          </label>
        </BaseTooltip>
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
    suggestion: {
      type: Object,
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
    getSuggestion(option) {
      return this.suggestion?.getSuggestion(option.value);
    },
    getScore(option) {
      return this.getSuggestion(option)?.score?.toFixed(1);
    },
    getAgent(option) {
      return this.getSuggestion(option)?.agent;
    },
    getTooltipText(option) {
      const title = `<span class="tooltip__title">${$nuxt.$t(
        "suggestion.name"
      )}</span>`;
      const agent = this.getAgent(option) ? `${this.getAgent(option)}: ` : "";
      const score = this.getScore(option) || "";
      return `${title}${agent}${score}`;
    },
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

  &__suggestion-icon {
    flex-shrink: 0;
    width: 10px;
    height: 10px;
  }

  &.label-active {
    color: white;
    background: palette(purple, 200);
    box-shadow: none;
    &:hover {
      box-shadow: inset 0 -2px 6px 0 darken(palette(purple, 200), 8%);
      background: darken(palette(purple, 200), 4%);
    }
  }

  &:not(.label-active):hover {
    background: darken(palette(purple, 800), 5%);
    transition: all 0.2s ease-in-out;
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

:deep(.tooltip__title) {
  display: block;
  font-weight: lighter;
  @include font-size(12px);
}

[data-title] {
  position: relative;
  overflow: visible;
  @include tooltip-mini("top");
}
</style>
