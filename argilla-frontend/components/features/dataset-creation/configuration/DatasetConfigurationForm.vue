<template>
  <section class="config-form">
    <div class="config-form__header">
      <div class="config-form__selectors">
        <DatasetConfigurationSelector
          v-if="subsets"
          class="config-form__selector"
          :options="subsets"
          :value="selectedSubset.name"
          @onValueChange="$emit('change-subset', $event)"
        />
        <DatasetConfigurationSelector
          v-if="splits"
          class="config-form__selector"
          :options="splits"
          :value="selectedSplit.name"
          @onValueChange="$emit('change-split', $event)"
        />
      </div>

      <BaseButton class="config-form__button primary" @click="createDataset"
        >Create Dataset</BaseButton
      >
    </div>
    <div class="config-form__content">
      <div class="config-form__col-wrapper">
        <div class="config-form__col" v-if="fields.length">
          <div class="config-form__col__header">Fields</div>
          <div class="config-form__col__content">
            <draggable
              class="config-form__draggable-area"
              :list="fields"
              :group="{ name: 'fields' }"
            >
              <DatasetConfigurationField
                v-for="field in fields"
                :key="field.name"
                :field="field"
              />
            </draggable>
          </div>
        </div>
      </div>
      <div class="config-form__col-wrapper">
        <div class="config-form__col" v-if="questions.length">
          <div class="config-form__col__header">Questions</div>
          <div class="config-form__col__content">
            <draggable
              class="config-form__draggable-area"
              :list="fields"
              :group="{ name: 'questions' }"
            >
              <DatasetConfigurationQuestion
                v-for="question in questions"
                :key="question.name"
                :question="question"
                :remove-is-allowed="true"
                @remove="selectedSubset.removeQuestion(question.name)"
              />
            </draggable>
            <DatasetConfigurationAddQuestion
              :options="[
                'no mapping',
                'text',
                'label_selection',
                'multi_label_selection',
                'rating',
                'ranking',
                'span',
              ]"
              @add-question="addQuestion($event)"
            />
          </div>
        </div>
      </div>
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
    subsets: {
      type: Array,
    },
    selectedSubset: {
      type: Object,
    },
    splits: {
      type: Array,
    },
    selectedSplit: {
      type: Object,
    },
  },
  methods: {
    createDataset() {
      console.log("Open dataset creation modal");
    },
    addQuestion(type) {
      const questionName = `${type}_${this.selectedSubset.questions.length}`;
      this.selectedSubset.addQuestion(questionName, type);
    },
  },
  mounted() {
    console.log(this.selectedSubset);
  },
};
</script>

<style lang="scss" scoped>
.config-form {
  display: flex;
  flex-direction: column;
  gap: $base-space;
  padding: $base-space $base-space * 2 $base-space * 2 0;
  height: 100%;
  &__header {
    display: flex;
    gap: $base-space;
    align-items: center;
    justify-content: space-between;
  }
  &__selectors {
    display: flex;
    gap: $base-space;
  }
  &__selector.selector {
    :deep(.dropdown__header) {
      background: var(--bg-opacity-4);
      min-height: $base-space * 5;
      border: none;
    }
  }
  &__content {
    display: flex;
    gap: $base-space * 2;
    min-height: 0;
  }
  &__col-wrapper {
    width: 100%;
  }
  &__col {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--bg-accent-grey-1);
    border: 1px solid var(--bg-opacity-6);
    border-radius: $border-radius-m;
    &__header {
      padding: $base-space * 2;
      font-weight: 500;
    }
    &__content {
      display: flex;
      flex-direction: column;
      padding: calc($base-space / 2) $base-space * 2 $base-space * 2;
      gap: $base-space;
      overflow: auto;
      height: 100%;
    }
  }
  &__draggable-area {
    display: flex;
    flex-direction: column;
    gap: $base-space;
  }
}
</style>
