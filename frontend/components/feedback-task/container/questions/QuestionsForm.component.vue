<template>
  <form
    class="questions-form"
    :class="questionFormClass"
    @submit.prevent="onSubmit"
    v-click-outside="onClickOutside"
    @click="focusOnFirstQuestionFromOutside"
  >
    <div class="questions-form__content">
      <div class="questions-form__header">
        <p class="questions-form__guidelines-link">
          <NuxtLink
            :to="{
              name: 'dataset-id-settings',
              params: { id: datasetId },
            }"
            target="_blank"
            >Annotation guidelines <svgicon name="external-link" width="12" />
          </NuxtLink>
        </p>
      </div>

      <QuestionsComponent
        :questions="record.questions"
        :autofocusPosition="autofocusPosition"
        @on-focus="updateQuestionAutofocus"
      />
    </div>
    <div class="footer-form">
      <div class="footer-form__content">
        <BaseButton
          v-if="!record.isDiscarded || isDiscarding"
          type="button"
          class="button--discard"
          @on-click="onDiscard"
          :title="$t('shortcuts.questions_form.discard')"
        >
          <span>Discard <span class="button__shortcuts" v-text="'⌫'" /></span>
        </BaseButton>
        <BaseButton
          type="button"
          class="button--draft"
          @on-click="onSaveDraft"
          :disabled="isSaveDraftButtonDisabled"
          :title="$t('shortcuts.questions_form.draft')"
        >
          <span
            >Save as draft
            <span class="button__shortcuts" v-text="'ctrl'" />+<span
              class="button__shortcuts"
              v-text="'S'"
          /></span>
        </BaseButton>
        <BaseButton
          type="submit"
          class="button--submit"
          :disabled="isSubmitButtonDisabled"
          :title="
            isSubmitButtonDisabled
              ? $t('to_submit_complete_required')
              : $t('shortcuts.questions_form.submit')
          "
        >
          <span>Submit <span class="button__shortcuts" v-text="'↵'" /></span>
        </BaseButton>
      </div>
    </div>
  </form>
</template>

<script>
import "assets/icons/external-link";
import "assets/icons/refresh";

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
      autofocusPosition: 0,
      interactionCount: 0,
      isTouched: false,
      userComesFromOutside: false,
    };
  },
  setup() {
    return useQuestionFormViewModel();
  },
  computed: {
    questionFormClass() {
      if (this.isSubmitting) return "--submitting --waiting";
      if (this.isDiscarding) return "--discarding --waiting";
      if (this.isDraftSaving) return "--saving-draft";

      if (this.isTouched || (this.formHasFocus && this.interactionCount > 1))
        return "--focused-form";
    },
    formHasFocus() {
      return this.autofocusPosition || this.autofocusPosition == 0;
    },
    numberOfQuestions() {
      return this.record.questions.length;
    },
    questionAreCompletedCorrectly() {
      return this.record.questionAreCompletedCorrectly();
    },
    isSubmitButtonDisabled() {
      return !this.questionAreCompletedCorrectly;
    },
    isSaveDraftButtonDisabled() {
      return false;
    },
  },
  watch: {
    record: {
      deep: true,
      immediate: true,
      handler() {
        this.isTouched = this.record.isSubmitted && this.record.isModified;
      },
    },
  },
  mounted() {
    document.addEventListener("keydown", this.handleGlobalKeys);
  },
  destroyed() {
    document.removeEventListener("keydown", this.handleGlobalKeys);
  },
  methods: {
    focusOnFirstQuestionFromOutside(event) {
      if (!this.userComesFromOutside) return;
      if (event.srcElement.id || event.srcElement.getAttribute("for")) return;

      this.userComesFromOutside = false;
      this.updateQuestionAutofocus(0);
    },
    focusOnFirstQuestion(event) {
      event.preventDefault();
      this.updateQuestionAutofocus(0);
    },
    onClickOutside() {
      this.autofocusPosition = null;
      this.userComesFromOutside = true;
    },
    handleGlobalKeys(event) {
      const { code, shiftKey, ctrlKey, metaKey } = event;

      if (code == "Tab" && this.userComesFromOutside) {
        this.focusOnFirstQuestion(event);

        return;
      }

      switch (code) {
        case "KeyS": {
          if (ctrlKey || metaKey) {
            event.preventDefault();
            event.stopPropagation();
            this.onSaveDraft();
          }
          break;
        }
        case "Enter": {
          if (shiftKey) this.onSubmit();
          break;
        }
        case "Backspace": {
          if (shiftKey) this.onDiscard();
          break;
        }
        default:
      }
    },
    async onDiscard() {
      if (this.record.isDiscarded) return;

      await this.discard(this.record);

      this.$emit("on-discard-responses");
    },
    async onSubmit() {
      if (this.isSubmitButtonDisabled) return;

      await this.submit(this.record);

      this.$emit("on-submit-responses");
    },
    onSaveDraft() {
      this.saveAsDraft(this.record);
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
  flex-basis: clamp(33%, 520px, 40%);
  max-height: 100%;
  min-width: 0;
  justify-content: space-between;
  border-radius: $border-radius-m;
  border: 1px solid transparent;
  background: palette(white);
  margin-bottom: auto;
  &__header {
    display: flex;
    justify-content: right;
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
    gap: $base-space * 2;
    padding: $base-space * 2;
    overflow: auto;
    scroll-behavior: smooth;
  }
  &.--pending {
    border-color: $black-10;
  }
  &.--draft,
  &.--saving-draft {
    border-color: $draft-color;
  }
  &.--discarded,
  &.--discarding {
    border-color: $discarded-color;
  }
  &.--submitted,
  &.--submitting {
    border-color: $submitted-color;
  }
  &.--saving-draft {
    box-shadow: 0 0 0 1px $draft-color;
  }
  &.--discarding {
    box-shadow: 0 0 0 1px $discarded-color;
  }
  &.--submitting {
    box-shadow: 0 0 0 1px $submitted-color;
  }
  &.--waiting .questions-form__content {
    opacity: 0.7;
  }
}

.footer-form {
  &__content {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    button {
      &:first-of-type {
        border-bottom-left-radius: 8px;
      }
      &:last-of-type {
        border-bottom-right-radius: 8px;
      }
    }
  }
}

.button {
  &__shortcuts {
    @include font-size(12px);
    color: rgb(255 255 255);
    background: #ffffff33;
    border-radius: 5px;
    padding: 0 3px;
    margin-right: 3px;
  }
  &--submit,
  &--draft,
  &--discard {
    width: 100%;
    justify-content: space-around;
    border-radius: 0;
    &:disabled {
      opacity: 0.7;
      pointer-events: visible;
      cursor: not-allowed;
    }
  }
  &--submit {
    background: $submitted-color;
    color: palette(white);
  }
  &--draft {
    background: $draft-color;
    color: palette(white);
  }
  &--discard {
    background: $discarded-color;
    color: palette(white);
  }
}

.draft {
  position: absolute;
  right: $base-space * 2;
  top: $base-space;
  user-select: none;
  display: flex;
  flex-direction: row;
  gap: 5px;
  align-items: center;
  margin: 0;
  @include font-size(12px);
  color: $black-37;
  font-weight: 500;
  p {
    margin: 0;
    &:hover {
      .tooltip {
        opacity: 1;
        height: auto;
        width: auto;
        overflow: visible;
      }
    }
  }
  .tooltip {
    opacity: 0;
    height: auto;
    width: 0;
    @extend %tooltip;
    top: 50%;
    transform: translateY(-50%);
    right: calc(100% + 10px);
    overflow: hidden;
    &:before {
      position: absolute;
      @extend %triangle-right;
      left: 100%;
    }
  }
}
</style>
