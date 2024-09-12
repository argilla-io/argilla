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

            <div
              class="settings__edition-form__group --subcategories"
              v-if="
                question.isMultiLabelType ||
                question.isSingleLabelType ||
                question.isSpanType
              "
            >
              <label :for="`options-${question.id}`" v-text="$t('labels')" />
              <BaseSwitch
                v-if="question.isMultiLabelType"
                class="settings__edition-form__switch --subcategory"
                :id="`options-order-${question.id}`"
                v-model="question.settings.suggestionFirst"
                >{{ $t("suggestionFirst") }}</BaseSwitch
              >

              <BaseRangeSlider
                v-if="question.settings.shouldShowVisibleOptions"
                class="settings__edition-form__slider --subcategory"
                :id="`visible_options-${question.id}`"
                :min="3"
                :max="question.settings.options.length"
                v-model="question.settings.visible_options"
                >{{ $t("visibleLabels") }}</BaseRangeSlider
              >

              <label
                v-text="$t('order')"
                class="settings__edition-form__label --subcategory"
              />
              <draggable
                class="label__container"
                ghost-class="label__item__ghost"
                :list="question.settings.options"
                :group="{ name: question.name }"
                @end="question.reloadAnswerFromOptions()"
              >
                <div
                  v-for="option in question.settings.options"
                  :key="option.value"
                >
                  <label class="label__item">
                    <svgicon
                      width="6"
                      name="draggable"
                      :id="`${option.value}-icon`"
                    />
                    <span>{{ option.text }}</span>
                  </label>
                </div>
              </draggable>
            </div>

            <BaseSwitch
              v-if="question.isTextType"
              class="settings__edition-form__switch"
              :id="`use-markdown-${question.id}`"
              v-model="question.settings.use_markdown"
              >{{ $t("useMarkdown") }}</BaseSwitch
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
        :legend="$t('settings.uiPreview')"
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

    &__label {
      &.--subcategory {
        display: block;
        @include font-size(13px);
        color: var(--fg-primary);
      }
    }

    &__content {
      display: flex;
      flex-direction: column;
      gap: $base-space * 2;
      width: 100%;
      max-width: 800px;
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

    &__switch.re-switch {
      :deep(label) {
        color: var(--fg-primary);
      }
      @include media(">desktop") {
        :deep(label) {
          min-width: 180px;
        }
      }
      &.--subcategory {
        @include font-size(13px);
      }
    }

    &__slider {
      :deep(label) {
        color: var(--fg-primary);
        line-height: 1;
        margin-right: 1em;
      }
      @include media(">desktop") {
        :deep(label) {
          min-width: 180px;
          margin-right: 1em;
        }
      }
      &.--subcategory {
        @include font-size(13px);
        @include media(">desktop") {
          display: flex;
          align-items: center;
        }
      }
    }

    &__group {
      display: flex;
      flex-direction: column;
      width: 100%;
      gap: 12px;

      &.--subcategories {
        & > label:first-child {
          margin-bottom: $base-space * 2;
        }
        @include media(">desktop") {
          gap: 0;
        }
      }

      .--subcategory {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        @include media(">desktop") {
          flex-wrap: nowrap;
          height: 32px;
        }
      }

      & > label {
        width: fit-content;
        height: 14px;
        color: var(--fg-primary);
      }

      & input {
        display: flex;
        flex-direction: row;
        align-items: center;
        width: 100%;
        height: 24px;
        padding: 16px;
        background: var(--bg-accent-grey-2);
        color: var(--fg-primary);
        border: 1px solid var(--bg-opacity-20);
        border-radius: $border-radius;
        outline: 0;
        &:focus {
          border: 1px solid var(--bg-action);
        }
      }

      & textarea {
        resize: vertical;
        min-height: 50px;
        max-height: 300px;
        padding: 16px;
        background: var(--bg-accent-grey-2);
        color: var(--fg-primary);
        border: 1px solid var(--bg-opacity-20);
        border-radius: $border-radius;
        outline: 0;

        &:focus {
          border: 1px solid var(--bg-action);
        }
      }
    }

    &__footer {
      width: 100%;
      flex-direction: row;
      justify-content: flex-end;
      align-items: center;
      padding: $base-space * 2 0;
      border-bottom: 1px solid var(--bg-opacity-10);
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
      background: var(--bg-solid-grey-1);
      border-radius: $border-radius-m;
      margin: $base-space 0;
    }
  }
}

$label-color: var(--bg-solid-grey-2);
$label-dark-color: var(--fg-secondary);

.label__container {
  display: inline-flex;
  align-items: center;
  flex-wrap: wrap;
  gap: calc($base-space / 2);
}

.label__item {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: calc($base-space / 2);
  width: 100%;
  padding: calc($base-space / 4);
  border-radius: $border-radius-s;
  min-width: 50px;
  text-align: center;
  color: $label-dark-color;
  font-weight: 500;
  outline: none;
  border: 2px solid transparent;
  cursor: grab;
  user-select: none;
  transition: background 0.2s ease;
  @include font-size(12px);
  span {
    border-radius: calc($border-radius-s - 2px);
    background: var(--bg-opacity-6);
    padding: 2px 4px;
    line-height: 1.2;
  }
  svg {
    fill: var(--bg-opacity-20);
  }
  &:hover {
    background: $label-color;
    transition: background 0.2s ease;
  }

  &__ghost {
    opacity: 0.2;
  }
}
</style>
