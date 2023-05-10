<template>
  <div class="text_field_component">
    <div class="title-area --body1">
      <span v-text="title" />
    </div>
    <div class="content-area --body1" v-text="fieldText" />
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
    gap: $base-space;
    color: $black-37;
  }
  .content-area {
    white-space: pre-wrap;
  }
}
</style>
