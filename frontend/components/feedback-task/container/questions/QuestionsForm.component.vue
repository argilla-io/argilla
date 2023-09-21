<template>
  <form
    class="questions-form"
    :class="{
      '--focused-form': isFormTouched || (formHasFocus && interactionCount > 1),
    }"
    @submit.prevent="onSubmit"
    v-click-outside="onClickOutside"
    @click="focusOnFirstQuestionFromOutside"
  >
    <div class="questions-form__content">
      <div class="questions-form__header">
        <div class="draft">
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
        </div>
        <p class="questions-form__title --heading5 --medium">
          {{ $t("submit-your-feedback") }}
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
        :showSuggestion="record.isPending || record.isDraft"
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
      isFormTouched: false,
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
    questionAreCompletedCorrectly() {
      return this.record.questionAreCompletedCorrectly();
    },
    isSubmitButtonDisabled() {
      if (this.record.isSubmitted)
        return !this.isFormTouched || !this.questionAreCompletedCorrectly;

      return !this.questionAreCompletedCorrectly;
    },
  },
  watch: {
    isFormTouched(isFormTouched) {
      if (this.record.isSubmitted)
        this.emitIsQuestionsFormTouched(isFormTouched);
    },
    record: {
      deep: true,
      immediate: true,
      handler() {
        if (this.record.isModified) this.saveDraft(this.record);

        this.isFormTouched = this.record.isModified;
      },
    },
  },
  created() {
    this.record.initialize();
  },
  mounted() {
    document.addEventListener("keydown", this.handleGlobalKeys);
  },
  destroyed() {
    this.emitIsQuestionsFormTouched(false);

    document.removeEventListener("keydown", this.handleGlobalKeys);
  },
  methods: {
    focusOnFirstQuestionFromOutside(event) {
      if (!this.userComesFromOutside) return;
      if (event.srcElement.id || event.srcElement.getAttribute("for")) return;

      this.userComesFromOutside = false;
      this.focusOnFirstQuestion(event);
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
        this.focusOnFirstQuestionFromOutside(event);

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
    emitIsQuestionsFormTouched(isFormTouched) {
      this.$emit("on-question-form-touched", isFormTouched);

      this.$root.$emit("are-responses-untouched", !isFormTouched);
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
