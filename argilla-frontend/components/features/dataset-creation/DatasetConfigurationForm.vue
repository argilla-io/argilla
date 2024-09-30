<template>
  <section class="config-form">
    <div class="config-form__col-wrapper">
      <div class="config-form__col">
        <div class="config-form__col__header">Fields</div>
        <div class="config-form__col__content">
          <DatasetConfigurationCard
            v-for="field in fields"
            :key="field.name"
            :item="field"
            :typeOptions="['text', 'image', 'chat', 'custom', 'no mapping']"
          >
          </DatasetConfigurationCard>
        </div>
      </div>
    </div>
    <div class="config-form__col-wrapper">
      <div class="config-form__col">
        <div class="config-form__col__header">Questions</div>
        <div class="config-form__col__content">
          <template v-if="questions.length">
            <div v-for="question in questions" :key="question.name">
              {{ question }}
            </div>
          </template>
        </div>
      </div>
    </div>
    <div class="config-form__button-container">
      <BaseButton class="config-form__button primary" @click="createDataset"
        >Create Dataset</BaseButton
      >
    </div>
  </section>
</template>

<script>
export default {
  props: {
    fields: {
      type: Array,
      required: true,
    },
    questions: {
      type: Array,
    },
  },
  methods: {
    createDataset() {
      console.log("Creating dataset");
    },
  },
};
</script>

<style lang="scss" scoped>
.config-form {
  display: flex;
  gap: $base-space * 2;
  padding: $base-space * 2 $base-space * 2 $base-space * 2 0;
  &__col-wrapper {
    width: 100%;
  }
  &__col {
    background: var(--bg-accent-grey-1);
    border: 1px solid var(--bg-opacity-10);
    border-radius: $border-radius-m;
    &__header {
      padding: $base-space * 2;
    }
    &__content {
      display: flex;
      flex-direction: column;
      padding: 0 $base-space * 2 $base-space * 2;
      gap: $base-space;
    }
  }
}
</style>
