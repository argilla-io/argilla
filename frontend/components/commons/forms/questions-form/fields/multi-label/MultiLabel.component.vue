<template>
  <div class="wrapper">
    <QuestionHeaderComponent
      :question="question"
      :showSuggestion="showSuggestion"
    />

    <LabelSelectionComponent
      :componentId="question.id"
      v-model="question.answer.values"
      :maxOptionsToShowBeforeCollapse="maxOptionsToShowBeforeCollapse"
      :multiple="true"
    />
  </div>
</template>

<script>
export default {
  name: "MultiLabelComponent",
  props: {
    question: {
      type: Object,
      required: true,
    },
    showSuggestion: {
      type: Boolean,
      default: () => false,
    },
  },
  computed: {
    maxOptionsToShowBeforeCollapse() {
      return this.question.settings.visible_options ?? -1;
    },
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-direction: column;
  gap: $base-space;
}
</style>
