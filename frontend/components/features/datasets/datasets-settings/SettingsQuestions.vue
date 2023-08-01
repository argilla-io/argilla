<template>
  <div class="settings-questions__container">
    <div class="settings-questions__edition-form">
      <h2 class="--heading5 --semibold">Edit questions</h2>
      <div v-for="question in settings.questions" :key="question.id">
        <form
          @submit.prevent="onSubmit"
          class="settings-questions__edition-form-questions"
        >
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
    flex-wrap: wrap;
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
    width: 50%;

    &-questions {
      display: flex;
      flex-direction: column;
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

        font-family: "Inter";
        font-style: normal;
        font-weight: 400;
        font-size: 20px;
        line-height: 14px;
        display: flex;
        align-items: center;

        color: #545d84;

        flex: none;
        order: 10;
        flex-grow: 0;
      }

      & input {
        box-sizing: border-box;
        display: flex;
        flex-direction: row;
        align-items: center;
        padding: 16px;

        background: #ffffff;
        border: 1px solid rgba(0, 0, 0, 0.2);
        border-radius: 5px;

        flex: none;
        order: 11;
        flex-grow: 0;

        height: 24px;
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
    width: 50%;
    height: 100%;
    padding: $base-space * 3;
    box-shadow: $shadow;
    background: palette(white);
    border-radius: $border-radius-m;
    overflow: auto;
  }
}
</style>
