<template>
  <div class="wrapper">
    <QuestionHeaderComponent
      :title="title"
      :isRequired="isRequired"
      :tooltipMessage="description"
    />

    <div class="container">
      <RenderMarkdownBaseComponent
        v-if="visibleMarkdown"
        class="textarea--markdown"
        :markdown="value"
        @click.native="onChangeFocus(true)"
      />
      <ContentEditableFeedbackTask
        v-else
        class="textarea"
        :annotationEnabled="true"
        :annotations="[]"
        :defaultText="value"
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
  computed: {
    visibleMarkdown() {
      return this.useMarkdown && !this.isEditionModeActive && !this.isFocused;
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
    onChangeFocus(status) {
      this.isEditionModeActive = status;
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
    display: flex;
    flex: 1;
    flex-direction: column;
    padding: $base-space;
  }
}
</style>
