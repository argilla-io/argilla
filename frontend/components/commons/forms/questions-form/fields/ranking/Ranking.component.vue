<template>
  <div class="wrapper">
    <QuestionHeaderComponent
      :question="question"
      :showSuggestion="showSuggestion"
    />

    <DndSelectionComponent :ranking="ranking" @on-reorder="onChanged" />
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
  },
  data() {
    return {
      options: this.question.answer.values,
    };
  },
  computed: {
    optionsHasAllResponsesWithRank() {
      return this.options.every((option) => option.rank);
    },
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
