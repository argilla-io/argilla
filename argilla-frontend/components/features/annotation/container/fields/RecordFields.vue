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
      <SpanAnnotationImageField
        v-if="hasSpanQuestion(name)"
        :spanQuestion="getSpanQuestion(name)"
      />
    </div>
  </div>
</template>
<script>
import SpanAnnotationImageField from "./image-annotation/SpanAnnotationImageField.vue";
export default {
  components: { SpanAnnotationImageField },
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
