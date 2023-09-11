<template>
  <div class="wrapper">
    <QuestionHeaderComponent
      :question="question"
      :showSuggestion="showSuggestion"
    />
    <div
      class="container"
      ref="container"
      :class="classes"
      @focus="onFocus"
      :tabindex="isEditionModeActive ? '-1' : '0'"
      @keydown.enter.exact="onEditMode"
    >
      <RenderMarkdownBaseComponent
        v-if="question.settings.use_markdown && !isEditionModeActive"
        class="textarea--markdown"
        :markdown="question.answer.value"
        @click.native="onFocus"
      />
      <ContentEditableFeedbackTask
        v-else
        class="textarea"
        :value="question.answer.value"
        :originalValue="question.answer.originalValue"
        :placeholder="question.settings.placeholder"
        :isFocused="isFocused"
        @change-text="onChangeTextArea"
        @on-change-focus="onChangeFocus"
        @on-exit-edition-mode="onExitEditionMode"
      />
    </div>
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
    showSuggestion: {
      type: Boolean,
      default: () => false,
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
        this.isEditionModeActive = newValue;
      },
    },
  },
  methods: {
    onEditMode(event) {
      if (this.isExitedFromEditionModeWithKeyboard) {
        event.stopPropagation();
        event.preventDefault();
        this.isEditionModeActive = true;
      }
    },
    onExitEditionMode() {
      this.$refs.container.focus();
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

      if (this.isFocused && this.isExitedFromEditionModeWithKeyboard) {
        return "--focus";
      }

      return null;
    },
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-direction: column;
  gap: $base-space;
}

.container {
  display: flex;
  padding: $base-space;
  border: 1px solid $black-20;
  border-radius: $border-radius-s;
  min-height: 10em;
  background: palette(white);
  &.--editing {
    border-color: $primary-color;
  }
  &.--focus {
    outline: 2px solid palette(apricot);
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
