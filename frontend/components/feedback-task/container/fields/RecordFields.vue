<template>
  <div class="record">
    <slot name="fixed-header"></slot>
    <div class="record__content">
      <slot name="content-header"></slot>
      <div
        v-for="{ id, title, content, isTextType, settings } in fields"
        :key="id"
      >
        <TextFieldComponent
          v-if="isTextType"
          :title="title"
          :fieldText="content"
          :useMarkdown="settings.use_markdown"
          :stringToHighlight="searchValue"
        />
      </div>
    </div>
  </div>
</template>
<script>
export default {
  props: {
    fields: {
      type: Array,
      required: true,
    },
  },
  computed: {
    searchValue() {
      return this.$route.query?._search ?? "";
    },
  },
};
</script>

<style lang="scss" scoped>
.record {
  display: flex;
  flex-direction: column;
  background: palette(white);
  border: 1px solid palette(grey, 600);
  border-radius: $border-radius-m;
  min-height: 0;
  &__content {
    height: 100%;
    display: flex;
    flex-direction: column;
    overflow: auto;
    gap: $base-space * 2;
    padding: $base-space * 2;
    border-radius: $border-radius-m;
  }
}
</style>
