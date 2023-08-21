<template>
  <form
    ref="formRef"
    class="questions-form"
    :class="{ '--focused-form': formHasFocus && interactionCount > 1 }"
    @submit.prevent="onSubmit"
    v-click-outside="onClickOutside"
    @click="onClickForm"
  >
    <div class="questions-form__content">
      <div class="questions-form__header">
        <p class="questions-form__title --heading5 --medium">
          Submit your feedback
        </p>
        <p class="questions-form__guidelines-link">
          Read the
          <NuxtLink
            :to="{
              name: 'dataset-id-settings',
              params: { id: datasetId },
            }"
            target="_blank"
            >annotation guidelines <svgicon name="external-link" width="12" />
          </NuxtLink>
        </p>
      </div>
      <div
        class="form-group"
        v-for="(question, index) in record.questions"
        :key="question.id"
        @keydown.shift.arrow-down="
          updateQuestionAutofocus(autofocusPosition + 1)
        "
        @keydown.shift.arrow-up="updateQuestionAutofocus(autofocusPosition - 1)"
      >
        <TextAreaComponent
          v-if="question.isTextType"
          ref="text"
          :title="question.title"
          v-model="question.answer.value"
          :placeholder="question.settings.placeholder"
          :useMarkdown="question.settings.use_markdown"
          :hasSuggestion="!record.isSubmitted && question.matchSuggestion"
          :isRequired="question.isRequired"
          :description="question.description"
          :isFocused="checkIfQuestionIsFocused(index)"
          @on-focus="updateQuestionAutofocus(index)"
        />

        <SingleLabelComponent
          v-if="question.isSingleLabelType"
          ref="singleLabel"
          :questionId="question.id"
          :title="question.title"
          v-model="question.answer.values"
          :hasSuggestion="!record.isSubmitted && question.matchSuggestion"
          :isRequired="question.isRequired"
          :description="question.description"
          :visibleOptions="question.settings.visible_options"
          :isFocused="checkIfQuestionIsFocused(index)"
          @on-focus="updateQuestionAutofocus(index)"
          @on-user-answer="focusNext(index)"
        />

        <MultiLabelComponent
          v-if="question.isMultiLabelType"
          ref="multiLabel"
          :questionId="question.id"
          :title="question.title"
          v-model="question.answer.values"
          :hasSuggestion="!record.isSubmitted && question.matchSuggestion"
          :isRequired="question.isRequired"
          :description="question.description"
          :visibleOptions="question.settings.visible_options"
          :isFocused="checkIfQuestionIsFocused(index)"
          @on-focus="updateQuestionAutofocus(index)"
        />

        <RatingComponent
          v-if="question.isRatingType"
          ref="rating"
          :title="question.title"
          v-model="question.answer.values"
          :hasSuggestion="!record.isSubmitted && question.matchSuggestion"
          :isRequired="question.isRequired"
          :description="question.description"
          :isFocused="checkIfQuestionIsFocused(index)"
          @on-focus="updateQuestionAutofocus(index)"
          @on-user-answer="focusNext(index)"
        />

        <RankingComponent
          v-if="question.isRankingType"
          ref="ranking"
          :title="question.title"
          v-model="question.answer.values"
          :hasSuggestion="!record.isSubmitted && question.matchSuggestion"
          :isRequired="question.isRequired"
          :description="question.description"
          :isFocused="checkIfQuestionIsFocused(index)"
          @on-focus="updateQuestionAutofocus(index)"
        />
      </div>
    </div>
    <div class="footer-form">
      <div class="footer-form__left-footer">
        <BaseButton type="button" class="primary text" @click.prevent="onClear">
          <span v-text="'Clear'" />
        </BaseButton>
      </div>
      <div class="footer-form__right-area">
        <BaseButton
          type="button"
          class="primary outline"
          @on-click="onDiscard"
          :disabled="record.isDiscarded"
        >
          <span v-text="'Discard'" />
        </BaseButton>
        <BaseButton
          type="submit"
          class="primary"
          :disabled="isSubmitButtonDisabled"
        >
          <span v-text="'Submit'" />
        </BaseButton>
      </div>
    </div>
  </form>
</template>

<script>
import "assets/icons/external-link";
import { isEqual, cloneDeep } from "lodash";
import { useQuestionFormViewModel } from "./useQuestionsFormViewModel";

export default {
  name: "QuestionsFormComponent",
  props: {
    datasetId: {
      type: String,
      required: true,
    },
    record: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      originalRecord: null,
      autofocusPosition: 0,
      interactionCount: 0,
      userComesFromOutside: false,
    };
  },
  setup() {
    return useQuestionFormViewModel();
  },
  computed: {
    formHasFocus() {
      return this.autofocusPosition || this.autofocusPosition == 0;
    },
    numberOfQuestions() {
      return this.record.questions.length;
    },
    isFormUntouched() {
      return isEqual(this.originalRecord, this.record);
    },
    questionAreCompletedCorrectly() {
      return this.record.questionAreCompletedCorrectly();
    },
    isSubmitButtonDisabled() {
      if (this.record.isSubmitted)
        return this.isFormUntouched || !this.questionAreCompletedCorrectly;

      return !this.questionAreCompletedCorrectly;
    },
    formWrapper() {
      return this.$refs.formRef;
    },
  },
  watch: {
    isFormUntouched(isFormUntouched) {
      this.emitIsQuestionsFormUntouched(isFormUntouched);
    },
  },
  created() {
    this.record.restore();

    this.onReset();
  },
  mounted() {
    document.addEventListener("keydown", this.onPressKeyboardShortCut);

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
  destroyed() {
    this.emitIsQuestionsFormUntouched(true);
    document.removeEventListener("keydown", this.onPressKeyboardShortCut);
  },
  methods: {
    onClickForm(e) {
      if (!this.userComesFromOutside) return;
      if (e.srcElement.id || e.srcElement.getAttribute("for")) return;

      this.userComesFromOutside = false;
      this.focusOnFirstQuestion(e);
    },
    focusOn($event, node) {
      $event.preventDefault();
      node.focus();
    },
    focusOnFirstQuestion(e) {
      e.preventDefault();
      this.updateQuestionAutofocus(0);
    },
    focusOnLastQuestion(e) {
      e.preventDefault();
      this.updateQuestionAutofocus(this.numberOfQuestions);
    },
    focusNext(index) {
      this.updateQuestionAutofocus(index + 1);
    },
    onClickOutside() {
      this.autofocusPosition = null;
      this.userComesFromOutside = true;
    },
    onPressKeyboardShortCut({ code, shiftKey }) {
      if (!shiftKey) return;

      switch (code) {
        case "Enter": {
          this.onSubmit();
          break;
        }
        case "Space": {
          this.onClear();
          break;
        }
        case "Backspace": {
          this.onDiscard();
          break;
        }
        default:
      }
    },
    async onDiscard() {
      if (this.record.isDiscarded) return;

      await this.discard(this.record);

      this.$emit("on-discard-responses");

      this.onReset();
    },
    async onSubmit() {
      if (this.isSubmitButtonDisabled) return;

      await this.submit(this.record);

      this.$emit("on-submit-responses");

      this.onReset();
    },
    async onClear() {
      await this.clear(this.record);

      this.onReset();
    },
    onReset() {
      this.originalRecord = cloneDeep(this.record);
    },
    emitIsQuestionsFormUntouched(isFormUntouched) {
      this.$emit("on-question-form-touched", !isFormUntouched);

      this.$root.$emit("are-responses-untouched", isFormUntouched);
    },
    checkIfQuestionIsFocused(index) {
      return index === this.autofocusPosition;
    },
    updateQuestionAutofocus(index) {
      this.interactionCount++;
      this.autofocusPosition = Math.min(
        this.numberOfQuestions - 1,
        Math.max(0, index)
      );
    },
  },
};
</script>

<style lang="scss" scoped>
.questions-form {
  display: flex;
  flex-direction: column;
  flex-basis: 37em;
  height: 100%;
  min-width: 0;
  justify-content: space-between;
  border-radius: $border-radius-m;
  border: 1px solid transparent;
  background: palette(white);
  &__header {
    align-items: baseline;
  }
  &__title {
    margin: 0 0 calc($base-space / 2) 0;
    color: $black-87;
  }
  &__guidelines-link {
    margin: 0;
    @include font-size(14px);
    color: $black-37;
    a {
      color: $black-37;
      outline: 0;
      text-decoration: none;
      &:hover,
      &:focus {
        text-decoration: underline;
      }
    }
  }
  &__content {
    position: relative;
    display: flex;
    flex-direction: column;
    gap: $base-space * 4;
    padding: $base-space * 3;
    overflow: auto;
    scroll-behavior: smooth;
  }

  &.--pending {
    border-color: transparent;
    &:not(.--focused-form) {
      box-shadow: $shadow;
    }
  }
  &.--discarded {
    border-color: #c3c3c3;
  }
  &.--submitted {
    border-color: $primary-color;
  }
  &.--focused-form {
    border-color: palette(brown);
  }
}

.footer-form {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: $base-space * 2 $base-space * 3;
  border-top: 1px solid $black-10;
  &__left-area {
    display: inline-flex;
  }
  &__right-area {
    display: inline-flex;
    gap: $base-space * 2;
  }
}
</style>
