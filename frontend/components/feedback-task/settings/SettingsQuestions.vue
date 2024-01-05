<template>
  <SynchronizeScroll class="settings__container">
    <div class="settings__edition-form">
      <div class="settings__edition-form__content">
        <h2 class="--heading5 --medium" v-text="$t('settings.editQuestions')" />
        <div v-for="question in settings.questions" :key="question.id">
          <form
            @submit.prevent="onSubmit(question)"
            class="settings__edition-form__questions"
          >
            <div class="settings__edition-form__name">
              <h4 class="--body1 --medium" v-text="question.name" />
              <BaseBadge class="--capitalized" :text="`${$t(question.type)}`" />
            </div>

            <Validation
              :validations="question.validate().title"
              class="settings__edition-form__group"
            >
              <label :for="`title-${question.id}`" v-text="$t('title')" />
              <input
                type="type"
                :id="`title-${question.id}`"
                v-model="question.title"
              />
            </Validation>

            <Validation
              :validations="question.validate().description"
              class="settings__edition-form__group"
            >
              <label
                :for="`description-${question.id}`"
                v-text="$t('description')"
              />
              <textarea
                :id="`description-${question.id}`"
                v-model="question.description"
              />
            </Validation>

            <BaseSwitch
              v-if="question.isTextType"
              :id="`use-markdown-${question.id}`"
              v-model="question.settings.use_markdown"
              >{{ $t("useMarkdown") }}</BaseSwitch
            >

            <BaseRangeSlider
              v-if="
                !!question.settings.visible_options &&
                question.settings.options.length > 3
              "
              :id="`visible_options-${question.id}`"
              :min="3"
              :max="question.settings.options.length"
              v-model="question.settings.visible_options"
              >{{ $t("visibleOptions") }}</BaseRangeSlider
            >

            <div class="settings__edition-form__footer">
              <BaseButton
                type="button"
                class="secondary light small"
                @on-click="restore(question)"
                :disabled="!question.isModified"
              >
                <span v-text="$t('cancel')" />
              </BaseButton>
              <BaseButton
                type="submit"
                class="primary small"
                :disabled="!question.isModified || !question.isQuestionValid"
              >
                <span v-text="$t('update')" />
              </BaseButton>
            </div>
          </form>
        </div>
      </div>
    </div>
    <div class="settings__preview">
      <QuestionsComponent
        legend="UI preview"
        class="settings__preview__content"
        :questions="settings.questions"
      />
    </div>
  </SynchronizeScroll>
</template>

<script>
import { useSettingsQuestionsViewModel } from "./useSettingsQuestionsViewModel";

export default {
  name: "SettingsQuestions",
  props: {
    settings: {
      type: Object,
      required: true,
    },
  },
  methods: {
    onSubmit(question) {
      this.update(question);
    },
  },
  setup() {
    return useSettingsQuestionsViewModel();
  },
};
</script>
<style lang="scss" scoped>
.settings {
  &__container {
    display: flex;
    gap: $base-space * 4;
    height: 100%;
    flex-wrap: wrap;
    min-height: 0;
  }

  &__edition-form {
    display: flex;
    flex: 1;
    height: 100%;
    overflow: auto;
    padding-right: $base-space * 2;

    &__content {
      display: flex;
      flex-direction: column;
      gap: $base-space * 2;
      width: 100%;
      margin-top: $base-space;
    }

    &__questions {
      display: flex;
      flex-direction: column;
      gap: $base-space * 2;
    }

    &__name {
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: space-between;
      gap: $base-space * 2;
      h4 {
        margin: 0;
      }
      .badge {
        margin-inline: 0 auto;
      }
    }

    &__group {
      display: flex;
      flex-direction: column;
      width: 100%;
      gap: $base-space;

      & label {
        width: fit-content;
        height: 14px;
        color: $black-54;
      }

      & input {
        display: flex;
        flex-direction: row;
        align-items: center;
        width: 100%;
        height: 24px;
        padding: 16px;
        background: palette(white);
        border: 1px solid $black-20;
        border-radius: $border-radius;
        outline: 0;
        &:focus {
          border: 1px solid $primary-color;
        }
      }

      & textarea {
        resize: vertical;
        min-height: 100px;
        max-height: 300px;
        padding: 16px;
        background: palette(white);
        border: 1px solid $black-20;
        border-radius: $border-radius;
        outline: 0;

        &:focus {
          border: 1px solid $primary-color;
        }
      }
    }

    &__footer {
      width: 100%;
      flex-direction: row;
      justify-content: flex-end;
      align-items: center;
      padding: $base-space * 2 0;
      border-bottom: 1px solid $black-10;
      display: inline-flex;
      gap: $base-space;
    }
  }

  &__preview {
    flex-basis: 37em;
    flex-direction: column;
    height: 100%;
    overflow: auto;
    &__content {
      padding: $base-space * 3;
      background: palette(grey, 800);
      border-radius: $border-radius-m;
      margin: $base-space 0;
    }
  }
}
</style>
