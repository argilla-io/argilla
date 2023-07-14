<template>
  <div class="record">
    <StatusTag class="record__status" :title="recordStatus" />
    <div
      v-for="{ id, name, content, isTextType, settings } in fields"
      :key="id"
    >
      <TextFieldComponent
        v-if="isTextType"
        :title="name"
        :fieldText="content"
        :useMarkdown="settings.use_markdown"
      />
    </div>
  </div>
</template>

<script>
export default {
  props: {
    recordStatus: {
      type: String,
      required: true,
    },
    fields: {
      type: Array,
      required: true,
    },
  },
};
</script>

<style lang="scss" scoped>
.record {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: auto;
  gap: $base-space * 2;
  padding: $base-space * 2;
  background: palette(white);
  border: 1px solid palette(grey, 600);
  border-radius: $border-radius-m;
  &__status {
    display: inline-flex;
    margin-right: auto;
  }
}
</style>
