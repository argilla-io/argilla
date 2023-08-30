<template>
  <form
    class="questions-form"
    :class="{ '--edited-form': isFormTouched }"
    @submit.prevent="onSubmit"
  >
    <div class="questions-form__content">
      <div class="questions-form__header">
        <div class="draft">
          <p v-if="draftSaving">
            <svgicon color="#0000005e" name="refresh" />
            {{ $t("saving") }}
          </p>
          <p v-else-if="record.isSavedDraft">
            <svgicon color="#0000005e" name="check" />
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
import { computed, watch } from "vue";
import { useGlobalShortcuts } from "./useGlobalShortcuts";
import "assets/icons/external-link";
import "assets/icons/refresh";
import "assets/icons/check";

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
  emits: ["on-submit-responses", "on-discard-responses"],
  setup(props, { emit }) {
    props.record.restore();

    const {
      clear,
      submit,
      discard,
      saveDraft,
      draftSaving,
      saveDraftImmediately,
    } = useQuestionFormViewModel();

    // computed
    const isFormTouched = computed(() => {
      return props.record.isModified;
    });

    const questionAreCompletedCorrectly = computed(() => {
      return props.record.questionAreCompletedCorrectly();
    });

    const isSubmitButtonDisabled = computed(() => {
      if (props.record.isSubmitted)
        return !isFormTouched.value || !questionAreCompletedCorrectly.value;

      return !questionAreCompletedCorrectly.value;
    });

    // watch
    watch(
      props.record,
      () => {
        if (props.record.isModified) saveDraft(props.record);
      },
      {
        immediate: true,
        deep: true,
      }
    );

    // actions on questions
    const onSubmit = async () => {
      if (!questionAreCompletedCorrectly) return;

      await submit(props.record);

      emit("on-submit-responses");
    };

    const onDiscard = async () => {
      await discard(props.record);

      emit("on-discard-responses");
    };

    const onClear = async () => {
      await clear(props.record);
    };

    const onSaveDraftImmediately = async () => {
      await saveDraftImmediately(props.record);
    };

    // shortcuts
    useGlobalShortcuts(onSaveDraftImmediately, onSubmit, onClear, onDiscard);

    return {
      onSubmit,
      onDiscard,
      onClear,
      draftSaving,
      isFormTouched,
      isSubmitButtonDisabled,
    };
  },
  watch: {
    isFormTouched(isFormTouched) {
      this.emitIsQuestionsFormTouched(isFormTouched);
    },
  },
  destroyed() {
    this.emitIsQuestionsFormTouched(false);
  },
  methods: {
    emitIsQuestionsFormTouched(isFormTouched) {
      this.$emit("on-question-form-touched", isFormTouched);

      this.$root.$emit("are-responses-untouched", !isFormTouched);
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
    position: relative;
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

.draft {
  position: absolute;
  right: $base-space * 2;
  top: $base-space;
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
    &:before {
      position: absolute;
      @extend %triangle-right;
    }
  }
}
</style>
