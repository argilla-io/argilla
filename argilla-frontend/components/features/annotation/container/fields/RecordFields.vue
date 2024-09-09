<template>
  <div class="fields">
    <div
      v-for="{
        id,
        name,
        title,
        content,
        settings,
        isTextType,
        isImageType,
      } in fields"
      :class="[isImageType ? 'fields__container--image' : '']"
      :key="id"
    >
      <SpanAnnotationTextField
        v-if="hasSpanQuestion(name)"
        :id="`${id}-${record.id}-span-field`"
        :name="name"
        :title="title"
        :fieldText="content"
        :spanQuestion="getSpanQuestion(name)"
        :searchText="recordCriteria.committed.searchText.value.text"
      />
      <TextField
        v-else-if="isTextType"
        :name="name"
        :title="title"
        :fieldText="content"
        :useMarkdown="settings.use_markdown"
        :searchText="recordCriteria.committed.searchText.value.text"
      />
      <ImageField v-else :name="name" :title="title" :content="content" />
    </div>
  </div>
</template>
<script>
export default {
  props: {
    record: {
      type: Object,
    },
    fields: {
      type: Array,
      required: true,
    },
    recordCriteria: {
      type: Object,
      required: true,
    },
  },
  methods: {
    getSpanQuestion(fieldName) {
      return this.spanQuestions?.find((q) => q.settings.field === fieldName);
    },
    hasSpanQuestion(fieldName) {
      return !!this.getSpanQuestion(fieldName);
    },
  },
  computed: {
    spanQuestions() {
      return this.record?.questions.filter((q) => q.isSpanType);
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
