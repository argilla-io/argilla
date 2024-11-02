<template>
  <RatingShortcuts>
    <div class="wrapper">
      <QuestionHeaderComponent :question="question" />

      <RatingMonoSelectionComponent
        ref="ratingMonoSelectionRef"
        :suggestion="question.suggestion"
        v-model="question.answer.values"
        :isFocused="isFocused"
        @on-focus="onFocus"
        @on-selected="onSelected"
      />
    </div>
  </RatingShortcuts>
</template>

<script>
export default {
  name: "RatingComponent",
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
