<template>
  <div
    class="container"
    ref="container"
    :class="classes"
    @focus="onFocus"
    :tabindex="isEditionModeActive ? '-1' : '0'"
    @keydown.shift.enter.exact.prevent="onEditMode"
  >
    <MarkdownRenderer
      v-if="question.settings.use_markdown && !isEditionModeActive"
      class="textarea--markdown"
      :markdown="question.answer.value"
      @click.native="onFocus"
      role="textbox"
      :aria-label="question._title"
    />
    <ContentEditableFeedbackTask
      v-else
      class="textarea"
      :value="question.answer.value"
      :originalValue="question.answer.originalValue"
      :placeholder="question.settings.placeholder"
      :isFocused="isEditionModeActive"
      @change-text="onChangeTextArea"
      @on-change-focus="onChangeFocus"
      @on-exit-edition-mode="onExitEditionMode"
      role="textbox"
      :aria-label="question._title"
    />
  </div>
</template>

<script>
export default {
  name: "TextAreaComponent",
  props: {
    question: {
      type: Object,
      required: true,
    },
    isFocused: {
      type: Boolean,
      default: () => false,
    },
  },
  data: () => {
    return {
      isEditionModeActive: false,
      isExitedFromEditionModeWithKeyboard: false,
    };
  },
  watch: {
    isFocused: {
      immediate: true,
      handler(newValue) {
        if (this.question.isRequired && !this.question.isAnswered) {
          this.onChangeFocus(newValue);

          return;
        }

        if (newValue) {
          this.$nextTick(() => {
            this.onExitEditionMode();
          });
        }
      },
    },
  },
  methods: {
    onEditMode() {
      if (this.isExitedFromEditionModeWithKeyboard) {
        this.isEditionModeActive = true;
      }
    },
    onExitEditionMode() {
      this.$refs.container.focus({
        preventScroll: true,
      });
      this.isEditionModeActive = false;
      this.isExitedFromEditionModeWithKeyboard = true;
    },
    onChangeTextArea(newText) {
      const isAnyText = newText?.length;

      this.question.answer.value = isAnyText ? newText : "";

      if (this.question.isRequired) {
        this.$emit("on-error", !isAnyText);
      }
    },
    onChangeFocus(isFocus) {
      this.isEditionModeActive = isFocus;

      if (isFocus) {
        this.$emit("on-focus");
      }
    },
    onFocus(event) {
      if (event.defaultPrevented) return;

      this.isEditionModeActive = true;
      this.isExitedFromEditionModeWithKeyboard = false;
    },
  },
  computed: {
    classes() {
      if (this.isEditionModeActive) {
        return "--editing";
      }

      return null;
    },
  },
};
</script>

<style lang="scss" scoped>
.container {
  display: flex;
  min-height: 4em;
  padding: $base-space;
  border: 1px solid var(--bg-opacity-20);
  border-radius: $border-radius-s;
  background: var(--bg-accent-grey-2);
  outline: none;
  &.--editing {
    border-color: var(--fg-cuaternary);
    outline: 1px solid var(--fg-cuaternary);
  }
  &:focus {
    outline: 1px solid var(--bg-opacity-20);
  }
  &:focus:not(:focus-visible) {
    outline: none;
  }
  .content--exploration-mode & {
    border: none;
    padding: 0;
  }
}

.textarea {
  display: flex;
  flex: 0 0 100%;
  &--markdown {
    display: inline;
    flex: 1;
    padding: $base-space;
  }
}
</style>
