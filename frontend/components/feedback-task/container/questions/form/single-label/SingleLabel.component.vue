<template>
  <div class="wrapper">
    <QuestionHeaderComponent
      :question="question"
      :showSuggestion="showSuggestion"
    />

    <LabelSelectionComponent
      v-model="question.answer.values"
      :componentId="question.id"
      :maxOptionsToShowBeforeCollapse="maxOptionsToShowBeforeCollapse"
      :multiple="false"
      :isFocused="isFocused"
      @on-focus="onFocus"
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
    showSuggestion: {
      type: Boolean,
      default: () => false,
    },
    isFocused: {
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
  },
  watch: {
    "question.answer.values": {
      deep: true,
      handler(newOptions) {
        if (newOptions.some((option) => option.isSelected))
          this.$emit("on-user-answer");
      },
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
