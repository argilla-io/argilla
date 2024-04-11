<template>
  <form
    class="questions-form"
    :class="questionFormClass"
    @submit.stop.prevent=""
    v-click-outside="onClickOutside"
    @click="focusOnFirstQuestionFromOutside"
  >
    <div class="questions-form__content" v-show="false">
      <div class="questions-form__header">
        <p class="questions-form__guidelines-link">
          <NuxtLink
            :to="{
              name: 'dataset-id-settings',
              params: { id: datasetId },
            }"
            target="_blank"
            >{{ $t("annotationGuidelines") }}
            <svgicon name="external-link" width="12" />
          </NuxtLink>
        </p>
      </div>

      <QuestionsComponent
        :questions="record.questions"
        :autofocusPosition="autofocusPosition"
        :is-bulk-mode="isBulkMode"
        @on-focus="updateQuestionAutofocus"
      />
    </div>
    <div v-if="isRunningTransition" class="commands">
      <div class="commands__content">
        <div>
          <span class="font">Swipe left for Bad response</span>
          <div class="commands__content--buttons">
            <span class="dot swipeDotLeft" />
            <span class="handIcon swipeLeft" />
          </div>
        </div>

        <div>
          <span class="font">Swipe up to Discard</span>
          <div class="commands__content--buttons">
            <span class="dot swipeDotUp" />
            <span class="handIcon swipeUp" />
          </div>
        </div>

        <div>
          <span class="font">Swipe right for Right response</span>
          <div class="commands__content--buttons">
            <span class="dot swipeDotRight" />
            <span class="handIcon swipeRight" />
          </div>
        </div>
      </div>
    </div>
    <div class="footer-form" v-show="false">
      <div class="footer-form__content">
        <BaseButton
          type="submit"
          class="button--submit"
          :class="[
            isSubmitting ? '--button--submitting' : null,
            isDiscarding || isDraftSaving ? '--button--remove-bg' : null,
          ]"
          :loading-progress="progress"
          :disabled="
            !questionAreCompletedCorrectly || isSubmitDisabled || isSaving
          "
          :data-title="
            !isSaving
              ? !questionAreCompletedCorrectly && !isSubmitDisabled
                ? $t('to_submit_complete_required')
                : submitTooltip
              : null
          "
          @on-click="onSubmit"
        >
          <span>Bad</span>
          <span v-if="isRunningTransition" class="dot swipeDotLeft" />
          <span v-if="isRunningTransition" class="handIcon swipeLeft" />
        </BaseButton>
        <BaseButton
          v-if="showDiscardButton || isDiscarding"
          type="button"
          class="button--discard"
          :class="isDiscarding ? '--button--discarding' : null"
          :loading="isDiscarding"
          :loading-progress="progress"
          :disabled="isDiscardDisabled || isSaving"
          :data-title="!isSaving ? draftSavingTooltip : null"
          @on-click="onDiscard"
        >
          <span>Discard</span>
          <span v-if="isRunningTransition" class="dot swipeDotUp" />
          <span v-if="isRunningTransition" class="handIcon swipeUp" />
        </BaseButton>
        <BaseButton
          type="submit"
          class="button--submit"
          :class="[
            isSubmitting ? '--button--submitting' : null,
            isDiscarding || isDraftSaving ? '--button--remove-bg' : null,
          ]"
          :loading-progress="progress"
          :disabled="
            !questionAreCompletedCorrectly || isSubmitDisabled || isSaving
          "
          :data-title="
            !isSaving
              ? !questionAreCompletedCorrectly && !isSubmitDisabled
                ? $t('to_submit_complete_required')
                : submitTooltip
              : null
          "
          @on-click="onSubmit"
        >
          <span>Good</span>
          <span v-if="isRunningTransition" class="dot swipeDotRight" />
          <span v-if="isRunningTransition" class="handIcon swipeRight" />
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
      isRunningTransition: window.isRunningTransition ?? true,
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
    isRunningTransition() {
      window.isRunningTransition = this.isRunningTransition;
    },
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

    setTimeout(() => {
      this.isRunningTransition = false;
    }, 4500);

    this.$root.$on("swipeLeft", () => this.onSubmit());
    this.$root.$on("swipeRight", () => this.onSubmit());
    this.$root.$on("swipeUp", () => this.onDiscard());
  },
  destroyed() {
    document.removeEventListener("keydown", this.handleGlobalKeys);
  },
  methods: {
    async autoSubmitWithKeyboard() {
      if (!this.enableAutoSubmitWithKeyboard) return;
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
  gap: $base-space;
  max-height: 100%;
  min-width: 0;
  justify-content: space-between;
  margin-bottom: auto;
  @include media("<desktop") {
    justify-content: flex-start;
  }
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
        color: $black-54;
        transition: color 0.2s ease-in-out;
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
    align-items: stretch;
    border-radius: $border-radius-m;
    background: #f0f2fa;
    container-type: inline-size;
    &:hover {
      .button--submit:not(:hover) {
        background: transparent;
      }
    }
  }
}

.button {
  @include font-size(16px);
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
    min-height: $base-space * 10;
    border-radius: $border-radius-m - 1;
    padding: $base-space;
    &:hover {
      color: $black-87;
    }
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
    background: darken($submitted-color-light, 2%);
    &:active:not([disabled]),
    &.--button--submitting,
    &.--button--submitting:hover {
      background: $submitted-color-medium;
    }
    &.--button--remove-bg {
      background: transparent;
    }
  }
  &--draft {
    background: $draft-color-light;
    &:active:not([disabled]),
    &.--button--saving-draft,
    &.--button--saving-draft:hover {
      background: $draft-color-medium;
    }
  }
  &--discard {
    background: $discarded-color-light;
    &:active:not([disabled]),
    &.--button--discarding,
    &.--button--discarding:hover {
      background: $discarded-color-medium;
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

.dot {
  position: absolute;
  width: 20px;
  height: 20px;
  background: rgba(149, 147, 241, 0.8);
  border-radius: 40px;
  left: 40px;
  visibility: hidden;
}

.handIcon {
  background-image: url("https://i.postimg.cc/8556gm60/hand.png");
  background-repeat: no-repeat;
  background-position: center;
  width: 50px;
  height: 50px;
  transform-origin: 52% 62%;
}

.swipeDotLeft {
  animation: swipeDotLeft 2s 0.5s infinite;
}
.swipeLeft {
  animation: swipeHandLeft 2s infinite;
}

.swipeDotRight {
  animation: swipeDotRight 2s 0.5s infinite;
}
.swipeRight {
  animation: swipeHandRight 2s infinite;
}

.swipeDotUp {
  animation: swipeDotUp 2s 0.5s infinite;
}
.swipeUp {
  animation: swipeHandUp 2s infinite;
}

@keyframes swipeHandLeft {
  25% {
    transform: translate(20px) rotate(30deg);
  }
  50% {
    transform: translate(-20px) rotate(-15deg);
  }
  100% {
    transform: translate(0px) rotate(0);
  }
}

@keyframes swipeDotLeft {
  12% {
    visibility: visible;
    width: 40px;
  }
  25% {
    visibility: visible;
    transform: translate(-65px);
    width: 20px;
  }
  26% {
    visibility: hidden;
  }
}

@keyframes swipeHandRight {
  25% {
    transform: translate(-20px) rotate(-15deg);
  }
  50% {
    transform: translate(20px) rotate(30deg);
  }
  100% {
    transform: translate(0px) rotate(0);
  }
}

@keyframes swipeDotRight {
  0% {
    transform: translate(-40px);
    width: 20px;
  }
  25% {
    width: 50px;
    visibility: visible;
  }
  26% {
    visibility: hidden;
  }
}

@keyframes swipeHandUp {
  0% {
    transform: translate(-20px) rotate(90deg) translateX(20px);
  }
  100% {
    transform: translate(-20px) rotate(60deg) translateX(-15px);
  }
}

@keyframes swipeDotUp {
  0% {
    transform: translate(-20px) translateY(30px);
    height: 20px;
  }
  25% {
    transform: translate(-20px) translateY(-5px);
    height: 45px;
    visibility: visible;
  }
  26% {
    transform: translate(-20px) translateY(-5px);
    visibility: hidden;
  }
}

.font {
  color: white;
  font-weight: 600;
  font-size: 17px;
}

.commands {
  background: rgba(149, 147, 241, 0.5);
  position: absolute;
  width: 110vw;
  left: -20px;
  height: 100%;
  display: flex;
  align-items: center;
  top: 0;

  &__content {
    display: flex;
    flex-direction: column;
    align-content: center;
    flex-wrap: wrap;
    justify-content: space-around;
    align-items: center;
    height: 70%;
    width: 100%;

    &--buttons {
      margin-top: 20px;
      margin-left: 30%;
      position: relative;
      display: flex;
      gap: 1em;
    }
  }
}
</style>
