<template>
  <div>
    <p
      v-if="legend"
      class="questions__title --body3 --light"
      v-text="legend"
      :aria-label="legend"
    />
    <div
      class="questions"
      role="list"
      aria-label="List of annotation questions"
    >
      <div
        v-for="(question, index) in questions"
        :key="question.id"
        :aria-label="'Question: ' + question.name"
        @keydown.arrow-up.prevent="
          updateQuestionAutofocus(autofocusPosition - 1)
        "
        @keydown.arrow-down.prevent="
          updateQuestionAutofocus(autofocusPosition + 1)
        "
      >
        <TextAreaComponent
          v-if="question.isTextType"
          :question="question"
          :isFocused="checkIfQuestionIsFocused(index)"
          @on-focus="updateQuestionAutofocus(index)"
        />

        <SingleLabelComponent
          v-if="question.isSingleLabelType"
          ref="singleLabel"
          :visible-shortcuts="visibleShortcuts"
          :question="question"
          :isFocused="checkIfQuestionIsFocused(index)"
          @on-focus="updateQuestionAutofocus(index)"
          @on-user-answer="focusNext(index)"
        />

        <MultiLabelComponent
          v-if="question.isMultiLabelType"
          ref="multiLabel"
          :visible-shortcuts="visibleShortcuts"
          :question="question"
          :isFocused="checkIfQuestionIsFocused(index)"
          @on-focus="updateQuestionAutofocus(index)"
        />

        <RatingComponent
          v-if="question.isRatingType"
          ref="rating"
          :question="question"
          :isFocused="checkIfQuestionIsFocused(index)"
          @on-focus="updateQuestionAutofocus(index)"
          @on-user-answer="focusNext(index)"
        />

        <RankingComponent
          v-if="question.isRankingType"
          ref="ranking"
          :question="question"
          :isFocused="checkIfQuestionIsFocused(index)"
          @on-focus="updateQuestionAutofocus(index)"
        />

        <SpanComponent
          v-if="question.isSpanType"
          ref="span"
          :visible-shortcuts="visibleShortcuts"
          :question="question"
          :isFocused="checkIfQuestionIsFocused(index)"
          :enableSpanQuestionShortcutsGlobal="enableSpanQuestionShortcutsGlobal"
          @on-focus="updateQuestionAutofocus(index)"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { useQuestionsViewModel } from "./useQuestionsViewModel";
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
    autofocusPosition: {
      type: Number,
    },
    isBulkMode: {
      type: Boolean,
      default: false,
    },
    visibleShortcuts: {
      type: Boolean,
      default: true,
    },
  },
  computed: {
    questionsWithLoopMovement() {
      return ["singleLabel", "multiLabel", "rating", "ranking", "span"]
        .filter((componentType) => this.$refs[componentType])
        .map((componentType) => this.$refs[componentType][0].$el);
    },
  },
  mounted() {
    this.questionsWithLoopMovement.forEach((parent) => {
      parent.addEventListener("keydown", this.handleKeyboardToMoveLoop(parent));
    });
  },
  beforeDestroy() {
    this.questionsWithLoopMovement.forEach((parent) => {
      parent.removeEventListener(
        "keydown",
        this.handleKeyboardToMoveLoop(parent)
      );
    });
  },
  methods: {
    // This is terrible
    handleKeyboardToMoveLoop(parent) {
      return (e) => {
        if (e.key !== "Tab") return;
        const isShiftKeyPressed = e.shiftKey;

        const focusable = parent.querySelectorAll(
          'input[type="checkbox"], [tabindex="0"]'
        );
        const firstElement = focusable[0];
        const lastElement = focusable[focusable.length - 1];

        const isLastElementActive = document.activeElement === lastElement;
        const isFirstElementActive = document.activeElement === firstElement;

        if (!isShiftKeyPressed && isLastElementActive) {
          this.focusOn(e, firstElement);
        } else if (isShiftKeyPressed && isFirstElementActive) {
          this.focusOn(e, lastElement);
        } else {
          const index = Array.from(focusable).findIndex(
            (r) => r === document.activeElement
          );

          const nextElementToFocus = isShiftKeyPressed
            ? focusable[index - 1]
            : focusable[index + 1];

          this.focusOn(e, nextElementToFocus);
        }
      };
    },
    focusOnFirstQuestion(e) {
      e.preventDefault();
      this.updateQuestionAutofocus(0);
    },
    focusOnLastQuestion(e) {
      e.preventDefault();
      this.updateQuestionAutofocus(this.questions.length);
    },
    focusOn($event, node) {
      $event.preventDefault();
      node.focus();
    },
    focusNext(index) {
      this.updateQuestionAutofocus(index + 1);
    },
    updateQuestionAutofocus(index) {
      this.$emit("on-focus", index);
    },
    checkIfQuestionIsFocused(index) {
      return this.autofocusPosition === index;
    },
  },
  setup(props) {
    return useQuestionsViewModel(props);
  },
};
</script>

<style lang="scss" scoped>
.questions {
  display: flex;
  flex-direction: column;
  gap: $base-space * 4;
  &__title {
    color: var(--fg-tertiary);
    margin-top: 0;
    margin-bottom: $base-space * 3;
  }
}
</style>
