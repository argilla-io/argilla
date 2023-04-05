<template>
  <div class="wrapper">
    <div class="title-area --body1">
      <span
        :key="colorHighlight"
        v-text="title"
        v-required-field="isRequired ? { color: colorHighlight } : false"
      />

      <TooltipComponent
        v-if="isIcon"
        :message="tooltipMessage"
        direction="bottom"
      >
        <svgicon class="icon" name="info" width="22" height="22" />
      </TooltipComponent>
    </div>

    <div class="container">
      <Text2TextContentEditable
        :annotationEnabled="true"
        :annotations="[]"
        :defaultText="initialOutputs.text"
        :placeholder="initialOutputs.placeholder"
        :isShortcutToSave="false"
        @change-text="
          $emit('on-change-text-area', {
            text: $event,
            placeholder: initialOutputs.placeholder,
          })
        "
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
    initialOutputs: {
      type: Object,
      default: () => {
        return { text: "", placeholder: "" };
      },
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
      default: false,
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
  color: $black-37;
}

.container {
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
</style>
