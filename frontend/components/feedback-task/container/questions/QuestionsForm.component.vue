<template>
  <form
    class="questions-form"
    :class="questionFormClass"
    @submit.stop.prevent=""
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
            >annotation guidelines <svgicon name="external-link" width="12" />
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
          :class="isDiscarding ? '--button--discarding' : null"
          :disabled="!areActionsEnabled"
          :title="
            !areActionsEnabled
              ? $t('to_annotate_record_bulk_required')
              : $t('shortcuts.questions_form.discard')
          "
          @on-click="onDiscard"
        >
          <span class="button__shortcuts" v-text="'⌫'" /><span
            v-text="$t('questions_form.discard')"
          />
        </BaseButton>
        <BaseButton
          type="button"
          class="button--draft"
          :class="isDraftSaving ? '--button--saving-draft' : null"
          :disabled="!areActionsEnabled"
          :title="
            !areActionsEnabled
              ? $t('to_annotate_record_bulk_required')
              : $platform.isMac
              ? $t('shortcuts.questions_form.draft_mac')
              : $t('shortcuts.questions_form.draft')
          "
          @on-click="onSaveDraft"
        >
          <span
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
          :class="isSubmitting ? '--button--submitting' : null"
          :disabled="areQuestionsCompletedCorrectly || !areActionsEnabled"
          :title="
            !areActionsEnabled
              ? $t('to_annotate_record_bulk_required')
              : areQuestionsCompletedCorrectly
              ? $t('to_submit_complete_required')
              : $t('shortcuts.questions_form.submit')
          "
          @on-click="onSubmit"
        >
          <span class="button__shortcuts" v-text="'↵'" />
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
    areQuestionsCompletedCorrectly() {
      return !this.questionAreCompletedCorrectly;
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
    async autoSubmitWithKeyboard() {
      if (!this.record.isModified) return;
      if (this.record.questions.length > 1) return;

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
      const { code, ctrlKey, metaKey, shiftKey } = event;

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
          this.autoSubmitWithKeyboard();
          break;
        }
      }
    },
    onDiscard() {
      if (!this.areActionsEnabled) return;

      this.$emit("on-discard-responses");
    },
    onSubmit() {
      if (!this.areActionsEnabled || this.areQuestionsCompletedCorrectly)
        return;

      this.$emit("on-submit-responses");
    },
    onSaveDraft() {
      if (!this.areActionsEnabled) return;

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
  min-width: 0;
  justify-content: space-between;
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
    border-radius: $border-radius-m;
    border: 1px solid transparent;
    background: palette(white);
    .--pending & {
      border-color: $black-10;
    }
    .--draft &,
    .--saving-draft & {
      border-color: $draft-color;
    }
    .--discarded &,
    .--discarding & {
      border-color: $discarded-color;
    }
    .--submitted &,
    .--submitting & {
      border-color: $submitted-color;
    }
    .--saving-draft & {
      box-shadow: 0 0 0 1px $draft-color;
    }
    .--discarding & {
      box-shadow: 0 0 0 1px $discarded-color;
    }
    .--submitting & {
      box-shadow: 0 0 0 1px $submitted-color;
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
    align-items: center;
    border-radius: $border-radius-m;
    border: 1px solid #c6d1ff;
    background: #f5f7ff;
    transition: border-color 0.35s ease;
    container-type: inline-size;
    &:hover {
      border-color: transparent;
      transition: border-color 0.35s ease;
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
    border-color: $black-20;
    border-style: solid;
    box-sizing: content-box;
    color: $black-87;
    background: palette(white);
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
    color: $black-87;
    min-height: $base-space * 6;
    border-radius: $border-radius-m - 1;
    padding: $base-space * 2 $base-space;
    &:hover,
    &.--button--discarding {
      color: $black-87;
    }
    &:disabled {
      opacity: 0.7;
      pointer-events: visible;
      cursor: not-allowed;
    }
  }
  &--submit {
    &:hover:not([disabled]) {
      background: #b3c4ff;
    }
    &:active:not([disabled]),
    &.--button--submitting,
    &.--button--submitting:hover {
      background: $submitted-color;
    }
  }
  &--draft {
    &:hover:not([disabled]) {
      background: #b2e6ee;
    }
    &:active:not([disabled]),
    &.--button--saving-draft,
    &.--button--saving-draft:hover {
      background: $draft-color;
    }
  }
  &--discard {
    &:hover:not([disabled]) {
      background: #e0dddd;
    }
    &:active:not([disabled]),
    &.--button--discarding,
    &.--button--discarding:hover {
      background: $discarded-color;
    }
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
