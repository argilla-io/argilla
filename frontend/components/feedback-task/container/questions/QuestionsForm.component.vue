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
        <!-- <div class="draft">
          <p v-if="draftSaving">
            <svgicon color="#0000005e" name="refresh" />
            {{ $t("saving") }}
          </p>
          <p v-else-if="record.isDraft">
            {{ $t("saved") }}
            <BaseDate
              class="tooltip"
              :date="record.updatedAt"
              format="date-relative-now"
              :updateEverySecond="10"
            />
          </p>
        </div> -->
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
          type="button"
          class="primary text button--clear"
          @click.prevent="onClear"
          :title="$t('shortcuts.questions_form.clear')"
        >
          <span v-text="'Clear'" />
        </BaseButton>
        <BaseButton
          type="button"
          class="button--draft"
          @on-click="onSaveDraftImmediately"
          :disabled="isSaveDraftButtonDisabled"
          :title="$t('shortcuts.questions_form.draft')"
        >
          <span v-text="draftSaving ? 'Saving...' : 'Save draft'" />
        </BaseButton>
        <BaseButton
          type="button"
          class="button--discard"
          @on-click="onDiscard"
          :disabled="record.isDiscarded"
          :title="$t('shortcuts.questions_form.discard')"
        >
          <span v-text="'Discard'" />
        </BaseButton>
        <BaseButton
          type="submit"
          class="button--submit"
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
      if (this.isSubmitting) return "--submitted --waiting";
      if (this.isDiscarding) return "--discarded --waiting";

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
      if (this.record.isSubmitted)
        return !this.isTouched || !this.questionAreCompletedCorrectly;

      return !this.questionAreCompletedCorrectly;
    },
    isSaveDraftButtonDisabled() {
      if (this.record.isPending || this.record.isDraft)
        return !this.record.isModified;
      return !this.record.hasAnyQuestionAnswered;
    },
  },
  watch: {
    record: {
      deep: true,
      immediate: true,
      handler() {
        if (this.record.isModified) this.saveDraft(this.record);

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
            this.onSaveDraftImmediately();
          }
          break;
        }
        case "Enter": {
          if (shiftKey) this.onSubmit();
          break;
        }
        case "Space": {
          if (shiftKey) {
            event.preventDefault(); // TODO: Review this line
            this.onClear();
          }
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
    async onClear() {
      await this.clear(this.record);
    },
    async onSaveDraftImmediately() {
      await this.saveDraftImmediately(this.record);
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
  &.--pending {
    border-color: $draft-color;
  }
  &.--discarded {
    border-color: $discarded-color;
  }
  &.--submitted {
    border-color: $submitted-color;
  }
  &.--focused-form {
    border-color: palette(turquoise);
  }
  &.--waiting .questions-form__content {
    opacity: 0.7;
  }
}

.footer-form {
  padding: 0 $base-space * 3 $base-space * 2 $base-space * 3;
  &__content {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
}

.button {
  &--submit,
  &--draft,
  &--discard {
    width: 100%;
    justify-content: space-around;
    border-radius: 0;

    &:disabled {
      opacity: 0.3;
    }
  }
  &--clear {
    flex-shrink: 0;
    min-width: 50px;
  }
  &--submit {
    background: $submitted-color;
    color: palette(white);
    border-bottom-right-radius: $border-radius;
    border-top-right-radius: $border-radius;
  }
  &--draft {
    background: $draft-color;
    color: palette(white);
    border-bottom-left-radius: $border-radius;
    border-top-left-radius: $border-radius;
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
