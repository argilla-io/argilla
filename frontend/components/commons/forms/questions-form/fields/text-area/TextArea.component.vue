<template>
  <div>
    <div class="title-area">
      <div class="title-area">
        <span
          :key="colorHighlight"
          v-text="title"
          v-required-field="isRequired ? { color: colorHighlight } : false"
        />
      </div>
    </div>
    <Text2TextContentEditable
      :annotationEnabled="true"
      :annotations="[]"
      :defaultText="''"
      :placeholder="placeholder"
      @change-text="$emit('on-change-text-area', $event)"
    />
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
    output: {
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
    colorHighlight: {
      type: String,
      default: () => "black",
    },
  },
};
</script>

<style lang="scss" scoped></style>
