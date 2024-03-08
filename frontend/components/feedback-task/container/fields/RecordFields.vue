<template>
  <div class="fields">
    <div v-for="{ id, name, title, content, settings } in fields" :key="id">
      <SpanAnnotationTextFieldComponent
        v-if="hasSpanQuestion(name) && supportedSpanAnnotation && isFocusMode"
        :name="name"
        :title="title"
        :fieldText="content"
        :spanQuestion="getSpanQuestion(name)"
      />
      <TextFieldComponent
        v-else
        :title="title"
        :fieldText="content"
        :useMarkdown="settings.use_markdown"
        :stringToHighlight="searchValue"
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
    spanQuestions: {
      type: Array,
      default: () => [],
    },
    recordCriteria: {
      type: Object,
      required: true,
    },
  },
  methods: {
    getSpanQuestion(fieldName) {
      return this.spanQuestions.find((q) => q.settings.field === fieldName);
    },
    hasSpanQuestion(fieldName) {
      return !!this.getSpanQuestion(fieldName);
    },
  },
  computed: {
    searchValue() {
      return this.$route.query?._search ?? "";
    },
    supportedSpanAnnotation() {
      return !!CSS.highlights;
    },
    isFocusMode() {
      return this.recordCriteria.committed.page.isFocusMode;
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
