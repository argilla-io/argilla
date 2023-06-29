<template>
  <div class="wrapper">
    <QuestionHeaderComponent
      :title="title"
      :isRequired="isRequired"
      :tooltipMessage="description"
    />
    <DndSelectionComponent
      :ranking="ranking"
      @on-reorder="onChanged"
      @on-keyboard-selection="onChangedWithKeyboard"
      :isFocused="isFocused"
    />
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
    isFocused: {
      type: Boolean,
      default: () => false,
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
    event: "on-change",
  },
  data() {
    return {
      ranking: adaptQuestionsToSlots({ options: this.options }),
    };
  },
  computed: {
    optionsHasAllResponsesWithRank() {
      return this.options.every((option) => option.rank);
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
    onChangedWithKeyboard(value, rank) {
      const optionIndex = this.options.findIndex(
        (option) => option.value === value
      );
      this.options[optionIndex].rank = rank;
      this.$emit("on-change", this.options);
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
