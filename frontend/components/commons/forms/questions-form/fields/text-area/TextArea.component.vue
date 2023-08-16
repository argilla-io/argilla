<template>
  <div class="wrapper">
    <QuestionHeaderComponent
      :title="title"
      :isRequired="isRequired"
      :hasSuggestion="hasSuggestion"
      :tooltipMessage="description"
    />

    <div class="container" :class="isFocused ? '--focused' : null">
      <RenderMarkdownBaseComponent
        v-if="useMarkdown && !isFocused"
        class="textarea--markdown"
        :markdown="value"
        @click.native="setFocus(true)"
      />
      <ContentEditableFeedbackTask
        v-else
        class="textarea"
        :value="value"
        :placeholder="placeholder"
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
    title: {
      type: String,
      required: true,
    },
    value: {
      type: String,
      default: () => "",
    },
    placeholder: {
      type: String,
      default: () => "",
    },
    isRequired: {
      type: Boolean,
      default: () => false,
    },
    description: {
      type: String,
      default: () => "",
    },
    useMarkdown: {
      type: Boolean,
      default: () => false,
    },
    hasSuggestion: {
      type: Boolean,
      default: () => false,
    },
  },
  data: () => {
    return {
      isFocused: false,
    };
  },
  model: {
    prop: "value",
    event: "on-change-value",
  },
  methods: {
    onChangeTextArea(newText) {
      const isAnyText = newText?.length;
      this.$emit("on-change-value", isAnyText ? newText : "");

      if (this.isRequired) {
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
  gap: 12px;
}

.container {
  display: flex;
  padding: $base-space;
  border: 1px solid $black-20;
  border-radius: $border-radius-s;
  min-height: 10em;
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
    display: flex;
    flex: 1;
    flex-direction: column;
    padding: $base-space;
  }
}
</style>
