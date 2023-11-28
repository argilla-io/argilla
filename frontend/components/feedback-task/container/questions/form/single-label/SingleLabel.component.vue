<template>
  <div class="wrapper">
    <QuestionHeaderComponent :question="question" />

    <LabelSelectionComponent
      v-model="question.answer.values"
      :componentId="question.id"
      :suggestions="question.suggestion?.suggestedAnswer"
      :maxOptionsToShowBeforeCollapse="maxOptionsToShowBeforeCollapse"
      :multiple="false"
      :isFocused="isFocused"
      :showShortcutsHelper="showShortcutsHelper"
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
    showShortcutsHelper: {
      type: Boolean,
      default: () => false,
    },
  },
  computed: {
    maxOptionsToShowBeforeCollapse() {
      return this.question.settings.visible_options ?? -1;
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
