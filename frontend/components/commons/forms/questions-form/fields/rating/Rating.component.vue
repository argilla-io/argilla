<template>
  <RatingShortcuts>
    <div class="wrapper">
      <QuestionHeaderComponent
        :question="question"
        :showSuggestion="showSuggestion"
      />

      <RatingMonoSelectionComponent
        ref="ratingMonoSelectionRef"
        v-model="question.answer.values"
        :isFocused="isFocused"
        @on-focus="$emit('on-focus')"
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
    showSuggestion: {
      type: Boolean,
      default: () => false,
    },
    isFocused: {
      type: Boolean,
      default: () => false,
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
