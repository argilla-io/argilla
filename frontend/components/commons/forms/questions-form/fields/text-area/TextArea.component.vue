<template>
  <div class="wrapper">
    <QuestionHeaderComponent
      :question="question"
      :showSuggestion="showSuggestion"
    />

    <div class="container" :class="isFocused ? '--focused' : null">
      <RenderMarkdownBaseComponent
        v-if="question.settings.use_markdown && !isFocused"
        class="textarea--markdown"
        :markdown="question.answer.value"
        @click.native="setFocus(true)"
      />
      <ContentEditableFeedbackTask
        v-else
        class="textarea"
        :value="question.answer.value"
        :placeholder="question.settings.placeholder"
        @change-text="onChangeTextArea"
        @on-change-focus="setFocus"
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
  },
  data: () => {
    return {
      isFocused: false,
    };
  },
  methods: {
    onChangeTextArea(newText) {
      const isAnyText = newText?.length;

      this.question.answer.value = isAnyText ? newText : "";

      if (this.question.isRequired) {
        this.$emit("on-error", !isAnyText);
      }
    },
    setFocus(status) {
      this.isFocused = status;
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
  &.--focused {
    border-color: $primary-color;
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
