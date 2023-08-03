<template>
  <SynchronizeScroll class="settings-questions__container">
    <div class="settings-questions__edition-form">
      <h2 class="--heading5 --semibold">Edit questions</h2>
      <div v-for="question in settings.questions" :key="question.id">
        <form
          @submit.prevent="onSubmit(question)"
          class="settings-questions__edition-form-questions"
        >
          <div class="settings-questions__edition-form-name">
            <h4 class="--body1 --medium --capitalized" v-text="question.name" />
            <p class="badge --capitalized" v-html="question.type" />
          </div>
          <div class="settings-questions__edition-form-group">
            <label for="question.id">Title</label>
            <input type="type" id="question.id" v-model="question.title" />
          </div>

          <div class="settings-questions__edition-form-group">
            <label for="question.id">Description</label>
            <input type="text" v-model="question.description" />
          </div>

          <BaseSwitch
            v-if="question.isTextType"
            v-model="question.settings.use_markdown"
            >Use Markdown</BaseSwitch
          >
          <div v-if="question.settings.visible_options">
            <label for="question.id">Visible options</label>
            <BaseRangeSlider
              :min="3"
              :max="question.settings.options.length"
              v-model="question.settings.visible_options"
            />
          </div>

          <div class="settings-questions__edition-form-footer">
            <BaseButton
              type="button"
              class="secondary light small"
              @on-click="restore(question)"
              :disabled="!question.isModified"
            >
              <span v-text="'Cancel'" />
            </BaseButton>
            <BaseButton
              type="submit"
              class="primary small"
              :disabled="!question.isModified"
            >
              <span v-text="'Update'" />
            </BaseButton>
          </div>
        </form>
      </div>
    </div>
    <QuestionsComponent
      legend="Ui preview"
      class="settings-questions__preview"
      :questions="settings.questions"
    />
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
.settings-questions {
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
    flex-direction: column;
    gap: $base-space * 2;
    height: 100%;
    overflow: auto;
    padding-right: $base-space * 2;

    &-questions {
      display: flex;
      flex-direction: column;
      gap: $base-space * 2;
    }

    &-name {
      display: flex;
      flex-direction: row;
      align-items: center;
      gap: $base-space * 2;
      h4 {
        margin: 0;
      }
    }

    &-group {
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
        box-sizing: border-box;
        display: flex;
        flex-direction: row;
        align-items: center;
        height: 24px;
        padding: 16px;
        background: #ffffff;
        border: 1px solid rgba(0, 0, 0, 0.2);
        border-radius: 5px;
      }
    }

    &-footer {
      width: 100%;
      display: flex;
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
    padding: $base-space * 3;
    box-shadow: $shadow;
    background: palette(grey, 800);
    border-radius: $border-radius-m;
    overflow: auto;
  }
}
</style>
