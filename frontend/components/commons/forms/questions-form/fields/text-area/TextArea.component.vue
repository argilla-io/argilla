<template>
  <div class="wrapper">
    <div class="title-area --body2">
      <span
        :key="colorHighlight"
        v-text="title"
        v-optional-field="isRequired ? false : true"
      />

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
      <Text2TextContentEditable
        class="textarea"
        :annotationEnabled="true"
        :annotations="[]"
        :defaultText="initialOptions.text"
        :placeholder="placeholder"
        :isShortcutToSave="false"
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
    initialOptions: {
      type: Object,
      default: () => {
        return { text: "", value: "" };
      },
    },
    optionId: {
      type: String,
      default: () => "optionId",
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
    colorHighlight: {
      type: String,
      default: () => "black",
    },
  },
  data: () => {
    return {
      isFocused: false,
    };
  },
  methods: {
    onChangeTextArea(newText) {
      this.$emit("on-change-text-area", [
        {
          id: this.optionId,
          text: newText,
          value: newText.length ? newText : null,
        },
      ]);

      const isAnyText = newText?.length;
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
  gap: $base-space;
}
.title-area {
  display: flex;
  align-items: center;
  gap: $base-space;
  color: $black-87;
  font-weight: 500;
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
}

.icon-info {
  display: inline-flex;
  margin: 0;
  padding: 0;
  overflow: inherit;
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
