<template>
  <div class="fields">
    <div
      v-for="{ id, title, content, isTextType, settings } in fields"
      :key="id"
    >
      <SpanAnnotationTextFieldComponent
        v-if="isTextType"
        :title="title"
        :fieldText="content"
        :spanQuestion="spanQuestion"
      />
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
    spanQuestion: {
      type: Object,
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
.fields {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: $base-space;
  min-width: 0;
  height: 100%;
  min-height: 0;
}
</style>
