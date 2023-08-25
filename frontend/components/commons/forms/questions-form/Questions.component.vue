<template>
  <div>
    <p v-if="legend" class="questions__title --body3 --light" v-text="legend" />
    <div class="questions">
      <div v-for="question in questions" :key="question.id">
        <TextAreaComponent
          v-if="question.isTextType"
          :question="question"
          :showSuggestion="showSuggestion"
        />

        <SingleLabelComponent
          v-if="question.isSingleLabelType"
          :question="question"
          :showSuggestion="showSuggestion"
        />

        <MultiLabelComponent
          v-if="question.isMultiLabelType"
          :question="question"
          :showSuggestion="showSuggestion"
        />

        <RatingComponent
          v-if="question.isRatingType"
          :question="question"
          :showSuggestion="showSuggestion"
        />

        <RankingComponent
          v-if="question.isRankingType"
          :question="question"
          :showSuggestion="showSuggestion"
        />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "QuestionsComponent",
  props: {
    questions: {
      type: Array,
      required: true,
    },
    legend: {
      type: String,
    },
    showSuggestion: {
      type: Boolean,
      default: () => false,
    },
  },
};
</script>

<style lang="scss" scoped>
.questions {
  display: flex;
  flex-direction: column;
  gap: $base-space * 4;
  &__title {
    color: $black-37;
    margin-top: 0;
    margin-bottom: $base-space * 3;
  }
}
</style>
