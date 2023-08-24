<template>
  <div ref="formRef">
    <p v-if="legend" class="questions__title --body3 --light" v-text="legend" />
    <div class="questions">
      <div
        v-for="(question, index) in questions"
        :key="question.id"
        @keydown.shift.arrow-up="updateQuestionAutofocus(autofocusPosition - 1)"
        @keydown.shift.arrow-down="
          updateQuestionAutofocus(autofocusPosition + 1)
        "
      >
        <TextAreaComponent
          v-if="question.isTextType"
          ref="text"
          :question="question"
          :showSuggestion="showSuggestion"
          :isFocused="checkIfQuestionIsFocused(index)"
          @on-focus="updateQuestionAutofocus(index)"
        />

        <SingleLabelComponent
          v-if="question.isSingleLabelType"
          ref="singleLabel"
          :question="question"
          :showSuggestion="showSuggestion"
          :isFocused="checkIfQuestionIsFocused(index)"
          @on-focus="updateQuestionAutofocus(index)"
          @on-user-answer="focusNext(index)"
        />

        <MultiLabelComponent
          ref="multiLabel"
          v-if="question.isMultiLabelType"
          :question="question"
          :showSuggestion="showSuggestion"
          :visibleOptions="question.settings.visible_options"
          :isFocused="checkIfQuestionIsFocused(index)"
          @on-focus="updateQuestionAutofocus(index)"
        />

        <RatingComponent
          v-if="question.isRatingType"
          ref="rating"
          :question="question"
          :showSuggestion="showSuggestion"
          :isFocused="checkIfQuestionIsFocused(index)"
          @on-focus="updateQuestionAutofocus(index)"
          @on-user-answer="focusNext(index)"
        />

        <RankingComponent
          v-if="question.isRankingType"
          ref="ranking"
          :question="question"
          :showSuggestion="showSuggestion"
          :isFocused="checkIfQuestionIsFocused(index)"
          @on-focus="updateQuestionAutofocus(index)"
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
    autofocusPosition: {
      type: Number,
    },
  },
  mounted() {
    const keyBoardHandler = (parent) => (e) => {
      const focusable = parent.querySelectorAll(
        'input[type="checkbox"], [tabindex="0"]'
      );

      const firstElement = focusable[0];
      const lastElement = focusable[focusable.length - 1];

      const isShiftKeyPressed = e.shiftKey;

      const isArrowDownPressed = e.key === "ArrowDown";
      const isArrowUpPressed = e.key === "ArrowUp";
      const activeElementIsInForm = this.formWrapper.contains(
        document.activeElement
      );
      const isLastElementActive = document.activeElement === lastElement;
      const isFirstElementActive = document.activeElement === firstElement;

      if (!activeElementIsInForm && isShiftKeyPressed && isArrowDownPressed) {
        this.focusOnFirstQuestion(e);
        return;
      }

      if (!activeElementIsInForm && isShiftKeyPressed && isArrowUpPressed) {
        this.focusOnLastQuestion(e);
        return;
      }

      if (e.key !== "Tab") return;
      // TODO: Move to Single and Multi label component
      // Is for manage the loop focus.
      if (!isShiftKeyPressed && isLastElementActive) {
        this.focusOn(e, firstElement);
      }
      if (isShiftKeyPressed && isFirstElementActive) {
        this.focusOn(e, lastElement);
      }
    };

    const initEventListenerFor = (aParent, aTypeOfComponent) => {
      const parent = this.$refs[aTypeOfComponent][0].$el;

      aParent.addEventListener("keydown", keyBoardHandler(parent));
    };

    ["text", "singleLabel", "multiLabel", "rating", "ranking"].forEach(
      (componentType) =>
        this.$refs[componentType] && initEventListenerFor(parent, componentType)
    );
  },
  computed: {
    formWrapper() {
      return this.$refs.formRef;
    },
  },
  methods: {
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
