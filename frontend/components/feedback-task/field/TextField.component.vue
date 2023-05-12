<template>
  <div class="text_field_component">
    <div class="title-area --body1">
      <span v-text="title" />
      <BaseActionTooltip tooltip="Copied" tooltip-position="left">
        <BaseButton
          title="Copy to clipboard"
          class="text_field_component__copy-button"
          @click.prevent="$copyToClipboard(fieldText)"
        >
          <svgicon name="copy" width="16" height="16" />
        </BaseButton>
      </BaseActionTooltip>
    </div>
    <transition name="fade" :key="fieldText" appear>
      <div class="content-area --body1" v-if="fieldText" v-text="fieldText" />
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
    fieldText: {
      type: String,
      required: true,
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
  border-radius: $border-radius;
  .title-area {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: $base-space;
    color: $black-37;
  }
  .content-area {
    white-space: pre-wrap;
  }
  &__copy-button {
    padding: 0;
    z-index: 2;
  }
}
.fade-enter-active,
.fade-leave-active {
  transition: all 1s;
}
.fade-enter,
.fade-leave-to {
  opacity: 0;
}
</style>
