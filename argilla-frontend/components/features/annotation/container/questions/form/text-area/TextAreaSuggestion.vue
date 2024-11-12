<template>
  <div class="container">
    <MarkdownRenderer
      class="textarea--markdown"
      :markdown="question.suggestion?.value"
    />
    <BaseActionTooltip :tooltip="$t('copied')" class="button-copy">
      <BaseButton @on-click="$copyToClipboard(question.suggestion?.value)">
        <svgicon name="copy" width="16" height="16" />
      </BaseButton>
    </BaseActionTooltip>
  </div>
</template>

<script>
import "assets/icons/copy";
export default {
  name: "TextAreaComponent",
  props: {
    question: {
      type: Object,
      required: true,
    },
  },
};
</script>

<style lang="scss" scoped>
.container {
  position: relative;
  display: flex;
  padding: $base-space * 2;
  border: 1px solid var(--bg-opacity-20);
  border-radius: $border-radius-s;
  background: var(--bg-accent-grey-2);
  min-height: 5em;
  &:hover {
    .button-copy {
      display: block;
    }
  }
}
.button-copy {
  display: none;
  position: absolute;
  right: $base-space * 2;
  bottom: $base-space * 2;
  .button {
    padding: 0;
  }
  .svg-icon {
    color: var(--fg-tertiary);
  }
}
</style>
