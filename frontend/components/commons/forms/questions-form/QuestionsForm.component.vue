<template>
  <form
    :key="renderForm"
    class="questions-form"
    :class="{ '--edited-form': !isFormUntouched }"
    @submit.prevent="onSubmit"
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
        v-for="question in record.questions"
        :key="question.id"
        @keydown.shift.arrow-down="
          updateQuestionAutofocus(autofocusPosition + 1)
        "
        @keydown.shift.arrow-up="updateQuestionAutofocus(autofocusPosition - 1)"
      >
        <TextAreaComponent
          v-if="question.isTextType"
          :title="question.title"
          :placeholder="question.settings.placeholder"
          v-model="question.answer.value"
          :useMarkdown="question.settings.use_markdown"
          :hasSuggestion="!record.isSubmitted && question.hasSuggestion"
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
          :hasSuggestion="!record.isSubmitted && question.hasSuggestion"
          :isRequired="question.isRequired"
          :description="question.description"
          :visibleOptions="question.settings.visible_options"
          :isFocused="checkIfQuestionIsFocused(index)"
          @on-focus="updateQuestionAutofocus(index)"
        />

        <MultiLabelComponent
          v-if="question.isMultiLabelType"
          ref="multiLabel"
          :questionId="question.id"
          :title="question.title"
          v-model="question.answer.values"
          :hasSuggestion="!record.isSubmitted && question.hasSuggestion"
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
          :hasSuggestion="!record.isSubmitted && question.hasSuggestion"
          :isRequired="question.isRequired"
          :description="question.description"
          :isFocused="checkIfQuestionIsFocused(index)"
          @on-focus="updateQuestionAutofocus(index)"
        />

        <RankingComponent
          v-if="question.isRankingType"
          ref="ranking"
          :title="question.title"
          :hasSuggestion="!record.isSubmitted && question.hasSuggestion"
          :isRequired="question.isRequired"
          :description="question.description"
          v-model="question.answer.values"
          :isFocused="checkIfQuestionIsFocused(index)"
          @on-focus="updateQuestionAutofocus(index)"
        />
      </div>
    </div>
    <div class="footer-form">
      <div class="footer-form__left-footer">
        <BaseButton
          type="button"
          ref="clearButton"
          class="primary text"
          @click.prevent="onClear"
        >
          <span v-text="'Clear'" />
        </BaseButton>
      </div>
      <div class="footer-form__right-area">
        <BaseButton
          type="button"
          ref="discardButton"
          class="primary outline"
          @on-click="onDiscard"
          :disabled="record.isDiscarded"
        >
          <span v-text="'Discard'" />
        </BaseButton>
        <BaseButton
          ref="submitButton"
          type="submit"
          name="submitButton"
          value="submitButton"
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
      renderForm: 0,
      autofocusPosition,
    };
  },
  setup() {
    return useQuestionFormViewModel();
  },
  computed: {
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
  },
  watch: {
    isFormUntouched(isFormUntouched) {
      this.emitIsQuestionsFormUntouched(isFormUntouched);
    },
  },
  created() {
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

      const isShiftkeyPressed = e.shiftKey;
      const isTabPressed = e.key === "Tab";
      const isLastElementActive = document.activeElement === lastElement;
      const isFirstElementActive = document.activeElement === firstElement;

      if (!isTabPressed) return;

      if (!isShiftkeyPressed && isLastElementActive) {
        e.preventDefault();
        firstElement.focus();
      } else if (isShiftkeyPressed && isFirstElementActive) {
        e.preventDefault();
        lastElement.focus();
      }
    };

    const initEventListenerFor = (aParent, aTypeOfComponent) => {
      const parent = this.$refs[aTypeOfComponent][0].$el;

      aParent.addEventListener("keydown", keyBoardHandler(parent));
    };

    ["singleLabel", "multiLabel", "rating", "ranking"].forEach(
      (componentType) =>
        this.$refs[componentType] && initEventListenerFor(parent, componentType)
    );
  },
  destroyed() {
    this.emitIsQuestionsFormUntouched(true);
    document.removeEventListener("keydown", this.onPressKeyboardShortCut);
  },
  methods: {
    onPressKeyboardShortCut({ code, shiftKey }) {
      switch (code) {
        case "Enter": {
          const elem = this.$refs.submitButton.$el;
          shiftKey && elem.click();
          break;
        }
        case "Space": {
          const elem = this.$refs.clearButton.$el;
          shiftKey && elem.click();
          break;
        }
        case "Backspace": {
          const elem = this.$refs.discardButton.$el;
          shiftKey && elem.click();
          break;
        }
        default:
      }
    },
    async onDiscard() {
      try {
        await this.discard(this.record);

        this.$emit("on-discard-responses");

        this.onReset();
      } catch (error) {
        console.log(error);
      }
    },
    async onSubmit() {
      if (!this.questionAreCompletedCorrectly) {
        return;
      }

      try {
        await this.submit(this.record);

        this.$emit("on-submit-responses");

        this.onReset();
      } catch (error) {
        console.log(error);
      }
    },
    async onClear() {
      try {
        await this.clear(this.record);

        this.onReset();
      } catch (err) {
        console.log(err);
      }
    },
    onReset() {
      this.originalRecord = cloneDeep(this.record);
      this.renderForm++;
    },
    emitIsQuestionsFormUntouched(isFormUntouched) {
      this.$emit("on-question-form-touched", !isFormUntouched);

      this.$root.$emit("are-responses-untouched", isFormUntouched);
    },
    checkIfQuestionIsFocused(index) {
      return this.record.isPending && index === this.autofocusPosition;
    },
    updateQuestionAutofocus(index) {
      const numberOfQuestions = this.record.questions.length;
      this.autofocusPosition = Math.min(
        numberOfQuestions - 1,
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
  box-shadow: $shadow;
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
  }
  &.--edited-form {
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
