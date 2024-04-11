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
      this.question.answer.value = "left";
      console.log("swipeLeft");
    },
    swipeToRight() {
      this.question.answer.value = "right";
      console.log("swipeRight");
    },
    swipeToUp() {
      console.log("swipeUP");
      //DISCARD!
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
