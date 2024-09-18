<template>
  <form
    class="questions-form"
    :class="questionFormClass"
    @submit.stop.prevent=""
    v-click-outside="onClickOutside"
    @click="focusOnFirstQuestionFromOutside"
  >
    <div class="questions-form__content">
      <QuestionsComponent
        :questions="record.questions"
        :autofocusPosition="autofocusPosition"
        :is-bulk-mode="isBulkMode"
        @on-focus="updateQuestionAutofocus"
      />
    </div>
    <div class="footer-form">
      <div class="footer-form__content">
        <BaseButton
          v-if="showDiscardButton || isDiscarding"
          type="button"
          class="button--discard"
          :class="isDiscarding ? '--button--discarding' : null"
          :loading="isDiscarding"
          :loading-progress="progress"
          :disabled="isDiscardDisabled || isSaving || !record.id"
          :data-title="!isSaving ? draftSavingTooltip : null"
          @on-click="onDiscard"
        >
          <span
            v-if="!isDiscarding"
            class="button__shortcuts"
            v-text="'⌫'"
          /><span v-text="$t('questions_form.discard')" />
        </BaseButton>
        <BaseButton
          type="button"
          class="button--draft"
          :class="isDraftSaving ? '--button--saving-draft' : null"
          :loading="isDraftSaving"
          :loading-progress="progress"
          :disabled="isDraftSaveDisabled || isSaving || !record.id"
          :data-title="!isSaving ? draftSavingTooltip : null"
          @on-click="onSaveDraft"
        >
          <span v-if="!isDraftSaving"
            ><span
              class="button__shortcuts"
              v-text="$platform.isMac ? '⌘' : 'ctrl'" /><span
              class="button__shortcuts"
              v-text="'S'"
          /></span>
          <span v-text="$t('questions_form.draft')" />
        </BaseButton>
        <BaseButton
          type="submit"
          class="button--submit"
          :class="[
            isSubmitting ? '--button--submitting' : null,
            isDiscarding || isDraftSaving ? '--button--remove-bg' : null,
          ]"
          :loading-progress="progress"
          :loading="isSubmitting"
          :disabled="
            !questionAreCompletedCorrectly ||
            isSubmitDisabled ||
            isSaving ||
            !record.id
          "
          :data-title="
            !!record.id
              ? !isSaving
                ? !questionAreCompletedCorrectly && !isSubmitDisabled
                  ? $t('to_submit_complete_required')
                  : submitTooltip
                : null
              : null
          "
          @on-click="onSubmit"
        >
          <span v-if="!isSubmitting" class="button__shortcuts" v-text="'↵'" />
          <span v-text="$t('questions_form.submit')" />
        </BaseButton>
      </div>
    </div>
  </form>
</template>

<script>
import "assets/icons/external-link";
import "assets/icons/refresh";

export default {
  props: {
    datasetId: {
      type: String,
      required: true,
    },
    record: {
      type: Object,
      required: true,
    },
    showDiscardButton: {
      type: Boolean,
      default: true,
    },
    areActionsEnabled: {
      type: Boolean,
      default: true,
    },
    isSubmitting: {
      type: Boolean,
      required: true,
    },
    isDiscarding: {
      type: Boolean,
      required: true,
    },
    isDraftSaving: {
      type: Boolean,
      required: true,
    },
    isSubmitDisabled: {
      type: Boolean,
      default: false,
    },
    isDiscardDisabled: {
      type: Boolean,
      default: false,
    },
    isDraftSaveDisabled: {
      type: Boolean,
      default: false,
    },
    submitTooltip: {
      type: String,
      default: null,
    },
    discardTooltip: {
      type: String,
      default: null,
    },
    draftSavingTooltip: {
      type: String,
      default: null,
    },
    progress: {
      type: Number,
      default: 0,
    },
    enableAutoSubmitWithKeyboard: {
      type: Boolean,
      default: false,
    },
    isBulkMode: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      autofocusPosition: 0,
      interactionCount: 0,
      isSubmittedTouched: false,
      userComesFromOutside: false,
    };
  },
  computed: {
    questionFormClass() {
      if (this.isSubmitting) return "--submitting --waiting";
      if (this.isDiscarding) return "--discarding --waiting";
      if (this.isDraftSaving) return "--saving-draft";

      if (
        this.isSubmittedTouched ||
        (this.formHasFocus && this.interactionCount > 1)
      )
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
    isSaving() {
      return this.isDraftSaving || this.isDiscarding || this.isSubmitting;
    },
  },
  watch: {
    record: {
      deep: true,
      immediate: true,
      handler() {
        this.isSubmittedTouched =
          this.record.isSubmitted && this.record.isModified;
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
    async autoSubmitWithKeyboard(key) {
      if (!this.enableAutoSubmitWithKeyboard) return;
      if (!this.record.isModified) return;
      if (this.record.questions.length > 1) return;
      if (isNaN(parseInt(key))) return;

      const question = this.record.questions[0];

      if (question.isSingleLabelType || question.isRatingType) {
        await this.onSubmit();
      }
    },
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
      const { code, ctrlKey, metaKey, shiftKey, key } = event;

      if (shiftKey) return;

      if (code === "Tab" && this.userComesFromOutside) {
        this.focusOnFirstQuestion(event);

        return;
      }

      if (!this.areActionsEnabled) return;

      switch (code) {
        case "KeyS": {
          if (this.$platform.isMac) {
            if (!metaKey) return;
          } else if (!ctrlKey) return;

          event.preventDefault();
          event.stopPropagation();
          this.onSaveDraft();

          break;
        }
        case "Enter": {
          this.onSubmit();
          break;
        }
        case "Backspace": {
          this.onDiscard();
          break;
        }
        default: {
          this.autoSubmitWithKeyboard(key);
          break;
        }
      }
    },
    onSubmit() {
      if (
        this.isSubmitDisabled ||
        this.isSaving ||
        !this.questionAreCompletedCorrectly
      )
        return;

      this.$emit("on-submit-responses");
    },
    onDiscard() {
      if (this.isDiscardDisabled || this.isSaving) return;

      this.$emit("on-discard-responses");
    },
    onSaveDraft() {
      if (this.isDraftSaveDisabled || this.isSaving) return;

      this.$emit("on-save-draft");
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
  gap: $base-space;
  max-height: 100%;
  min-width: 100%;
  justify-content: space-between;
  margin-bottom: auto;
  @include media("<desktop") {
    justify-content: flex-start;
  }
  &__content {
    position: relative;
    display: flex;
    flex-direction: column;
    gap: $base-space * 2;
    padding: $base-space * 2;
    overflow: auto;
    scroll-behavior: smooth;
    border-radius: $border-radius-m;
    border: 1px solid transparent;
    background: var(--bg-form);
    .--pending & {
      border-color: var(--bg-opacity-6);
    }
    .--draft &,
    .--saving-draft & {
      border-color: var(--fg-status-draft);
    }
    .--discarded &,
    .--discarding & {
      border-color: var(--fg-status-discarded);
    }
    .--submitted &,
    .--submitting & {
      border-color: var(--fg-status-submitted);
    }
    .--saving-draft & {
      box-shadow: 0 0 0 1px var(--fg-status-draft);
    }
    .--discarding & {
      box-shadow: 0 0 0 1px var(--fg-status-discarded);
    }
    .--submitting & {
      box-shadow: 0 0 0 1px var(--fg-status-submitted);
    }
    .--waiting & {
      opacity: 0.7;
    }
  }
}

.footer-form {
  &__content {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: stretch;
    border-radius: $border-radius-m;
    background: var(--bg-form-button-area);
    container-type: inline-size;
    &:hover {
      .button--submit:not(:hover) {
        background: transparent;
      }
    }
  }
}

.button {
  &__shortcuts {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    gap: 4px;
    height: $base-space * 2;
    border-radius: $border-radius;
    border-width: 1px 1px 3px 1px;
    border-color: var(--fg-shortcut-key);
    border-style: solid;
    box-sizing: content-box;
    color: var(--fg-primary);
    background: var(--bg-accent-grey-2);
    @include font-size(11px);
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
      "Open Sans", "Helvetica Neue", sans-serif;
    padding: 0 4px;
  }
  &__shortcuts-group {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 4px;
  }
  &--submit,
  &--draft,
  &--discard {
    width: 100%;
    justify-content: center;
    color: var(--fg-primary);
    min-height: $base-space * 6;
    border-radius: $border-radius-m - 1;
    padding: $base-space;
    &:disabled {
      pointer-events: visible;
      cursor: not-allowed;
      opacity: 1;
      & > * {
        opacity: 0.5;
      }
    }
  }
  &--submit {
    &:not([disabled]) {
      background: var(--bg-status-submitted);
    }
    &:hover:not([disabled]) {
      background: var(--bg-status-submitted-accent);
    }
    &:active:not([disabled]),
    &.--button--submitting,
    &.--button--submitting:hover {
      background: var(--bg-status-submitted-accent);
    }
    &.--button--remove-bg {
      background: transparent;
    }
  }
  &--draft {
    &:hover:not([disabled]) {
      background: var(--bg-status-draft);
    }
    &:active:not([disabled]),
    &.--button--saving-draft,
    &.--button--saving-draft:hover {
      background: var(--bg-status-draft-accent);
    }
  }
  &--discard {
    &:hover:not([disabled]) {
      background: var(--bg-status-discarded);
    }
    &:active:not([disabled]),
    &.--button--discarding,
    &.--button--discarding:hover {
      background: var(--bg-status-discarded-accent);
    }
  }
}

[data-title] {
  position: relative;
  overflow: visible;
  @include tooltip-mini("top");
}

@container (max-width: 500px) {
  .button {
    &--submit,
    &--draft,
    &--discard {
      flex-direction: column;
    }
  }
}
</style>
