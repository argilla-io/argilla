<template>
  <div class="wrapper">
    <QuestionHeaderComponent
      :title="title"
      :isRequired="isRequired"
      :hasSuggestion="hasSuggestion"
      :tooltipMessage="description"
    />

    <DndSelectionComponent :ranking="ranking" @on-reorder="onChanged" />
  </div>
</template>

<script>
import { adaptQuestionsToSlots } from "./ranking-adapter";

export default {
  name: "RankingComponent",
  props: {
    title: {
      type: String,
      required: true,
    },
    isRequired: {
      type: Boolean,
      default: false,
    },
    description: {
      type: String,
      default: "",
    },
    options: {
      type: Array,
      required: true,
    },
    hasSuggestion: {
      type: Boolean,
      default: () => false,
    },
  },
  model: {
    prop: "options",
    event: "on-change",
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
      this.$emit(
        "on-change",
        this.options.map((option) => ({
          ...option,
          rank: newQuestionRanked.getRanking(option),
        }))
      );
    },
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
