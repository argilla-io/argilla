<template>
  <div>
    <h2 class="--heading5 --semibold">Edit questions</h2>
    <div class="settings-questions__container">
      <div class="settings-questions__edition-form">
        <div v-for="question in settings.questions" :key="question.id">
          <form
            @submit.prevent="onSubmit"
            class="settings-questions__edition-form-questions"
          >
            <div class="settings-questions__edition-form-name">
              <h4
                class="--heading6 --semibold --capitalized"
                v-text="question.name"
              />
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

            <div class="settings-questions__edition-form-footer">
              <BaseButton type="button" class="primary outline">
                <span v-text="'Cancel'" />
              </BaseButton>
              <BaseButton type="submit" class="primary">
                <span v-text="'Update'" />
              </BaseButton>
            </div>
          </form>
        </div>
      </div>
      <QuestionsComponent
        class="settings-questions__preview"
        :questions="settings.questions"
      />
    </div>
  </div>
</template>

<script>
export default {
  name: "SettingsQuestions",
  props: {
    settings: {
      type: Object,
      required: true,
    },
  },
  methods: {
    onSubmit() {},
  },
};
</script>
<style lang="scss" scoped>
.settings-questions {
  &__container {
    display: flex;
    gap: $base-space * 2;
    height: 100%;
    width: 100%;
  }

  &__edition-form {
    display: flex;
    flex: 1;
    flex-direction: column;
    gap: $base-space * 2;
    height: 100%;

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
    }

    &-group {
      display: flex;
      flex-direction: column;
      width: 100%;
      gap: $base-space;

      & label {
        width: fit-content;
        height: 14px;
        color: #545d84;
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
      gap: $base-space * 2;
    }
  }

  &__preview {
    flex-basis: 37em;
    flex-direction: column;
    height: 100%;
    padding: $base-space * 3;
    box-shadow: $shadow;
    background: palette(white);
    border-radius: $border-radius-m;
    overflow: auto;
  }
}
</style>
