<template>
  <div class="wrapper">
    <QuestionHeaderComponent :question="question" />

    <LabelSelectionComponent
      :componentId="question.id"
      :suggestion="question.suggestion"
      :maxOptionsToShowBeforeCollapse="question.settings.visible_options"
      :suggestionFirst="question.settings.suggestionFirst"
      :multiple="true"
      :isFocused="isFocused"
      v-model="question.answer.values"
      @on-focus="onFocus"
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
    isFocused: {
      type: Boolean,
      default: () => false,
    },
  },
  methods: {
    onFocus() {
      this.$emit("on-focus");
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
