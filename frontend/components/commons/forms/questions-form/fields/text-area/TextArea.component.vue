<template>
  <div class="wrapper">
    <div class="title-area --body1 --medium">
      <span v-text="title" v-optional-field="isRequired ? false : true" />

      <BaseIconWithBadge
        class="icon-info"
        v-if="isIcon"
        icon="info"
        :id="`${title}TextArea`"
        :show-badge="false"
        iconColor="#acacac"
        badge-vertical-position="top"
        badge-horizontal-position="right"
        badge-border-color="white"
        v-tooltip="{ content: tooltipMessage, backgroundColor: '#FFF' }"
      />
    </div>

    <div class="container" :class="isFocused ? '--focused' : null">
      <BaseRenderMarkdownComponent
        v-if="useMarkdown && !isFocused"
        class="textarea--markdown"
        :markdown="value"
        @click.native="setFocus(true)"
      />
      <ContentEditableFeedbackTask
        v-else
        class="textarea"
        :annotationEnabled="true"
        :annotations="[]"
        :defaultText="value"
        :placeholder="placeholder"
        @change-text="onChangeTextArea"
        @on-change-focus="setFocus"
      />
    </div>
  </div>
</template>

<script>
import "assets/icons/info";

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
    isIcon: {
      type: Boolean,
      default: () => false,
    },
    tooltipMessage: {
      type: String,
      default: () => "",
    },
    useMarkdown: {
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
.title-area {
  color: $black-87;
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

.icon {
  color: $black-37;
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

.icon-info {
  display: inline-flex;
  width: 20px;
  height: 20px;
  margin: 0;
  padding: 0;
  overflow: inherit;
  vertical-align: middle;
  &[data-title] {
    position: relative;
    overflow: visible;
    &:before,
    &:after {
      margin-top: 0;
    }
  }
}
</style>
