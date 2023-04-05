<template>
  <div class="wrapper">
    <div class="title-area">
      <div class="title-area">
        <span
          :key="colorHighlight"
          v-text="title"
          v-required-field="isRequired ? { color: colorHighlight } : false"
        />
      </div>
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
    colorHighlight: {
      type: String,
      default: () => "black",
    },
  },
};
</script>

<style lang="scss" scoped>
.container {
  width: calc(100% - 200px);
  padding: $base-space;
  border: 1px solid $black-20;
  border-radius: $border-radius-s;
  &.--focused {
    border-color: $primary-color;
  }
  .content--exploration-mode & {
    border: none;
    padding: 0;
  }
}
</style>
