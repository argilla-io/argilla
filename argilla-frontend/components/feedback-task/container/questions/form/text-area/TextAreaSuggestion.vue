<template>
  <div class="container">
    <RenderMarkdownBaseComponent
      class="textarea--markdown"
      :markdown="question.suggestion?.suggestedAnswer"
    />
    <BaseActionTooltip tooltip="Copied" class="button-copy">
      <BaseButton
        @on-click="$copyToClipboard(question.suggestion?.suggestedAnswer)"
      >
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
  border: 1px solid $black-20;
  border-radius: $border-radius-s;
  min-height: 10em;
  background: palette(white);
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
    color: $black-37;
  }
}
</style>
