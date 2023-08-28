<template>
  <form
    class="questions-form"
    :class="{ '--focused-form': formHasFocus && interactionCount > 1 }"
    @submit.prevent="onSubmit"
    v-click-outside="onClickOutside"
    @click="focusOnFirstQuestionFromOutside"
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

      <QuestionsComponent
        :questions="record.questions"
        :showSuggestion="!record.isSubmitted"
        :autofocusPosition="autofocusPosition"
        @on-focus="updateQuestionAutofocus"
      />
    </div>
    <div class="footer-form">
      <div class="footer-form__left-footer">
        <BaseButton
          type="button"
          class="primary text"
          @click.prevent="onClear"
          :title="$t('shortcuts.questions_form.clear')"
        >
          <span v-text="'Clear'" />
        </BaseButton>
      </div>
      <div class="footer-form__right-area">
        <BaseButton
          type="button"
          class="primary outline"
          @on-click="onDiscard"
          :disabled="record.isDiscarded"
          :title="$t('shortcuts.questions_form.discard')"
        >
          <span v-text="'Discard'" />
        </BaseButton>
        <BaseButton
          type="submit"
          class="primary"
          :disabled="isSubmitButtonDisabled"
          :title="$t('shortcuts.questions_form.submit')"
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
    document.addEventListener("keydown", this.handleGlobalKeys);
  },
  destroyed() {
    this.emitIsQuestionsFormUntouched(true);
    document.removeEventListener("keydown", this.handleGlobalKeys);
  },
  methods: {
    focusOnFirstQuestionFromOutside(e) {
      if (!this.userComesFromOutside) return;
      if (e.srcElement.id || e.srcElement.getAttribute("for")) return;

      this.userComesFromOutside = false;
      this.focusOnFirstQuestion(e);
    },
    focusOnFirstQuestion(e) {
      e.preventDefault();
      this.updateQuestionAutofocus(0);
    },
    onClickOutside() {
      this.autofocusPosition = null;
      this.userComesFromOutside = true;
    },
    handleGlobalKeys(e) {
      const { code, shiftKey } = e;

      if (code == "Tab" && this.userComesFromOutside) {
        this.focusOnFirstQuestionFromOutside(e);

        return;
      }

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

// [data-title] {
//   position: relative;
//   overflow: visible;
//   @extend %has-tooltip--top;
//   &:before,
//   &:after {
//     margin-top: calc($base-space/2);
//   }
// }
</style>
