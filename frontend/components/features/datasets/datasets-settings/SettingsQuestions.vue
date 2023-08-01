<template>
  <div class="settings-questions__container">
    <div class="settings-questions__edition-form">
      <h2 class="--heading5 --semibold">Edit questions</h2>
      <form @submit.prevent="onSubmit">Formulario de edición</form>
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
  }
  &__edition-form {
    display: flex;
    flex: 1;
    flex-direction: column;
    gap: $base-space * 2;
    height: 100%;
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