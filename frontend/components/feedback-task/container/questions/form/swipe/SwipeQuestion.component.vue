<template>
  <div class="wrapper">
    <QuestionHeaderComponent :question="question" />
  </div>
</template>

<script>
import { useSwipeQuestionViewModel } from "./useSwipeQuestionViewModel";

export default {
  props: {
    question: {
      type: Object,
      required: true,
    },
  },
  methods: {
    swipeToLeft() {
      this.question.answer.values[0].isSelected = true;

      this.$root.$emit("swipeLeft");
    },
    swipeToRight() {
      this.question.answer.values[1].isSelected = true;

      this.$root.$emit("swipeRight");
    },
    swipeToUp() {
      this.$root.$emit("swipeUp");
    },
  },
  mounted() {
    this.handleSwipe(this.swipeToLeft, this.swipeToRight, this.swipeToUp);
  },
  setup() {
    return useSwipeQuestionViewModel();
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
