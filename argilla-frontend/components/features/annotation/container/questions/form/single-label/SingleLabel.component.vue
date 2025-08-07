<template>
  <div class="wrapper">
    <QuestionHeaderComponent :question="question" />

    <LabelSelectionComponent
      :visible-shortcuts="visibleShortcuts"
      :componentId="question.id"
      :suggestion="question.suggestion"
      :maxOptionsToShowBeforeCollapse="question.settings.visible_options"
      v-model="question.answer.values"
      :multiple="false"
      :isFocused="isFocused"
      :aria-role="'listbox'"
      :aria-multiselectable="false"
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
    visibleShortcuts: {
      type: Boolean,
      default: true,
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
  gap: $base-space * 1.5;
}
</style>
