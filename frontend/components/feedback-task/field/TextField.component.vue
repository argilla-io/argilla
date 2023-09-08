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
    <transition name="fade" v-if="fieldText" appear mode="out-in">
      <div class="content-area --body1" :key="fieldText">
        <div v-if="!useMarkdown" v-text="fieldText" />
        <RenderMarkdownBaseComponent v-else :markdown="text" />
      </div>
    </transition>
  </div>
</template>

<script>
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
  computed: {
    text() {
      if (this.stringToHighlight.length === 0) return this.fieldText;

      const regex = new RegExp(
        `\\b(${this.stringToHighlight.replace(/`/g, "\\`")})`,
        "gi"
      );

      const newText = this.fieldText.replace(regex, (match) =>
        this.htmlHighlightFor(match)
      );

      return newText;
    },
  },
  methods: {
    htmlHighlightFor(aText) {
      return `<span class="highlight-text">${aText}</span>`;
    },
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
