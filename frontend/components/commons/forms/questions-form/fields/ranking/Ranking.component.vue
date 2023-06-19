<template>
  <div class="wrapper">
    <QuestionHeaderComponent
      :title="title"
      :isRequired="isRequired"
      :tooltipMessage="description"
    />

    <DndSelectionComponent :ranking="ranking" @onChanged="onChanged" />
  </div>
</template>

<script>
import { adaptQuestionsToSots } from "./ranking-adapter";

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
  },
  model: {
    prop: "options",
  },
  data() {
    return {
      ranking: adaptQuestionsToSots({ options: this.options }),
    };
  },
  methods: {
    onChanged(newQuestionRanked) {
      this.options = this.options.map((option) => ({
        ...option,
        ranking: newQuestionRanked.getRanking(option),
      }));
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
