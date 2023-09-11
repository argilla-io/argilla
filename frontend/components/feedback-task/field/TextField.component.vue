<template>
  <div class="text_field_component">
    <div class="title-area --body2">
      <span v-text="title" />
      <BaseActionTooltip tooltip="Copied" tooltip-position="left">
        <BaseButton
          title="Copy to clipboard"
          class="text_field_component__copy-button"
          @click.prevent="$copyToClipboard(text)"
        >
          <svgicon color="#acacac" name="copy" width="18" height="18" />
        </BaseButton>
      </BaseActionTooltip>
    </div>
    <transition name="fade" v-if="text" appear mode="out-in">
      <div class="content-area --body1" :key="text">
        <div v-if="!useMarkdown" v-text="text" />
        <RenderMarkdownBaseComponent v-else :markdown="text" />
      </div>
    </transition>
  </div>
</template>

<script>
import { useTextFieldViewModel } from "./useTextFieldViewModel";
export default {
  name: "TextFieldComponent",
  props: {
    title: {
      type: String,
      required: true,
    },
    stringToHighlight: {
      type: String,
      default: "",
    },
    fieldText: {
      type: String,
      required: true,
    },
    useMarkdown: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    return useTextFieldViewModel(props);
  },
};
</script>

<style lang="scss" scoped>
.text_field_component {
  display: flex;
  flex-direction: column;
  gap: $base-space;
  padding: 2 * $base-space;
  background: palette(grey, 800);
  border-radius: $border-radius-m;
  .title-area {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: $base-space;
    color: $black-87;
  }
  .content-area {
    white-space: pre-wrap;
    word-break: break-word;
  }
  &__copy-button {
    padding: 0;
    z-index: 2;
  }
}
.fade-enter-active,
.fade-leave-active {
  transition: all 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
