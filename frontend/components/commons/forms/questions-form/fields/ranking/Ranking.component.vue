<template>
  <div class="wrapper">
    <QuestionHeaderComponent
      :question="question"
      :showSuggestion="showSuggestion"
    />
    <DndSelectionComponent
      :ranking="ranking"
      @on-reorder="onChanged"
      :isFocused="isFocused"
      @on-focus="onFocus"
    />
  </div>
</template>

<script>
import { adaptQuestionsToSlots } from "./ranking-adapter";

export default {
  name: "RankingComponent",
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
  data() {
    return {
      options: this.question.answer.values,
    };
  },
  computed: {
    ranking() {
      return adaptQuestionsToSlots({ options: this.options });
    },
  },
  methods: {
    onChanged(newQuestionRanked) {
      this.question.answer.values.forEach((option) => {
        option.rank = newQuestionRanked.getRanking(option);
      });

      this.options = this.question.answer.values;
    },
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
