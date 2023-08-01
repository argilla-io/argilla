<template>
  <div class="wrapper">
    <QuestionHeaderComponent
      :title="title"
      :isRequired="isRequired"
      :hasSuggestion="hasSuggestion"
      :tooltipMessage="description"
    />
    <div
      class="container"
      @focus="onFocus"
      :tabindex="isEditionModeActive ? '-1' : '0'"
    >
      <RenderMarkdownBaseComponent
        v-if="visibleMarkdown"
        class="textarea--markdown"
        :markdown="value"
        @click.native="onFocus"
      />
      <ContentEditableFeedbackTask
        v-else
        class="textarea"
        :value="value"
        :placeholder="placeholder"
        :isFocused="isFocused"
        @change-text="onChangeTextArea"
        @on-change-focus="onChangeFocus"
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
    isFocused: {
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
      isEditionModeActive: false,
    };
  },
  model: {
    prop: "value",
    event: "on-change-value",
  },
  watch: {
    isFocused: {
      immediate: true,
      handler(newValue) {
        this.isEditionModeActive = newValue;
      },
    },
  },
  computed: {
    visibleMarkdown() {
      return this.useMarkdown && !this.isEditionModeActive;
    },
  },
  methods: {
    onChangeTextArea(newText) {
      const isAnyText = newText?.length;
      this.$emit("on-change-value", isAnyText ? newText : "");

      if (this.isRequired) {
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
  &:focus-within {
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
