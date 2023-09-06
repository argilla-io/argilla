<template>
  <form
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

      <QuestionsComponent
        :questions="record.questions"
        :showSuggestion="!record.isSubmitted"
      />
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
    this.record.restore();

    this.onReset();
  },
  mounted() {
    document.addEventListener("keydown", this.onPressKeyboardShortCut);
  },
  destroyed() {
    this.emitIsQuestionsFormUntouched(true);
    document.removeEventListener("keydown", this.onPressKeyboardShortCut);
  },
  methods: {
    onPressKeyboardShortCut({ code, shiftKey }) {
      switch (code) {
        case "Enter": {
          this.onSubmit();
          break;
        }
        case "Space": {
          if (shiftKey) this.onClear();
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
      await this.discard(this.record);

      this.$emit("on-discard-responses");

      this.onReset();
    },
    async onSubmit() {
      if (!this.questionAreCompletedCorrectly) {
        return;
      }

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
      &:hover {
        text-decoration: underline;
      }
    }
  }
  &__content {
    display: flex;
    flex-direction: column;
    gap: $base-space * 4;
    padding: $base-space * 3;
    overflow: auto;
    scroll-behavior: smooth;
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
