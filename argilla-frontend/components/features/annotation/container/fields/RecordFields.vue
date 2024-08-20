<template>
  <div class="fields">
    <div v-for="{ id, name, title, content, settings } in fields" :key="id">
      <TextFieldComponent
        :name="name"
        :title="title"
        :fieldText="content"
        :useMarkdown="settings.use_markdown"
        :searchText="recordCriteria.committed.searchText.value.text"
        :record="record"
      />
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
