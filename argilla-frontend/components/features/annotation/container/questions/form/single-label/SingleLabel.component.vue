<template>
  <div class="wrapper">
    <QuestionHeaderComponent :question="question" />

    <LabelSelectionComponent
      :componentId="question.id"
      :suggestion="question.suggestion"
      :maxOptionsToShowBeforeCollapse="question.settings.visible_options"
      v-model="question.answer.values"
      :multiple="false"
      :isFocused="isFocused"
      @on-focus="onFocus"
      @on-selected="onSelected"
    />
  </div>
</template>

<script>
export default {
  name: "SingleLabelComponent",
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
    onSelected() {
      this.$emit("on-user-answer");
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
