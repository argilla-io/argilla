<template>
  <div class="wrapper">
    <QuestionHeaderComponent :question="question" />

    <LabelSelectionComponent
      :visible-shortcuts="visibleShortcuts"
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
    visibleShortcuts: {
      type: Boolean,
      default: true,
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
  gap: $base-space * 1.5;
}
</style>
