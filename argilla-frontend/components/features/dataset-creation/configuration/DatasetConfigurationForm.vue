<template>
  <section class="config-form">
    <div class="config-form__content">
      <div class="config-form__col-wrapper">
        <div
          class="config-form__col"
          v-if="dataset.selectedSubset.fields.length"
        >
          <div class="config-form__col__header">
            Fields
            <div class="config-form__subset" v-if="dataset.subsets.length > 1">
              Subset:
              <DatasetConfigurationSelector
                class="config-form__selector"
                :options="dataset.subsets"
                :value="dataset.selectedSubset.name"
                @onValueChange="$emit('change-subset', $event)"
              >
                <template slot="optionsIntro">
                  <span class="config-form__selector__intro"
                    >Your can create a dataset from only one subset.
                  </span>
                </template>
              </DatasetConfigurationSelector>
            </div>
          </div>
          <div class="config-form__col__content">
            <draggable
              class="config-form__draggable-area"
              :list="dataset.selectedSubset.fields"
              :group="{ name: 'fields' }"
              :disabled="isFocused"
            >
              <DatasetConfigurationField
                v-for="field in dataset.selectedSubset.fields.filter(
                  (f) => f.name !== dataset.mappings.external_id
                )"
                :key="field.name"
                :field="field"
                :available-types="availableFieldTypes"
                @is-focused="isFocused = $event"
              />
            </draggable>
          </div>
        </div>
      </div>
      <div class="config-form__col-wrapper">
        <div class="config-form__col">
          <div class="config-form__col__header">
            Questions
            <DatasetConfigurationAddQuestion
              :options="[
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
          <div class="config-form__col__content --questions">
            <draggable
              v-if="dataset.selectedSubset.questions.length"
              class="config-form__draggable-area"
              :list="dataset.selectedSubset.questions"
              :group="{ name: 'questions' }"
              :disabled="isFocused"
            >
              <DatasetConfigurationQuestion
                v-for="question in dataset.selectedSubset.questions"
                :key="question.name"
                :question="question"
                :columns="dataset.selectedSubset.columns"
                :remove-is-allowed="true"
                :available-types="availableQuestionTypes"
                @remove="dataset.selectedSubset.removeQuestion(question.name)"
                @change-type="onTypeIsChanged(question.name, $event)"
                @is-focused="isFocused = $event"
              />
            </draggable>
            <div class="config-form__button-area">
              <BaseButton
                class="primary"
                @click.prevent="
                  visibleDatasetCreationDialog = !visibleDatasetCreationDialog
                "
                >Create Dataset</BaseButton
              >
              <DatasetConfigurationDialog
                v-if="visibleDatasetCreationDialog"
                :dataset="dataset"
                :is-loading="isLoading"
                @close-dialog="visibleDatasetCreationDialog = false"
                @create-dataset="createDataset"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { useDatasetConfigurationForm } from "./useDatasetConfigurationForm";

export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      isFocused: false,
      visibleDatasetCreationDialog: false,
    };
  },
  methods: {
    createDataset() {
      this.create(this.dataset);
    },
    addQuestion(type) {
      const questionName = `${type} ${this.dataset.selectedSubset.questions.length}`;
      this.dataset.selectedSubset.addQuestion(questionName, { type });
    },
    onTypeIsChanged(name, type) {
      this.dataset.selectedSubset.addQuestion(name, {
        type: type.value,
      });
    },
  },
  setup() {
    return useDatasetConfigurationForm();
  },
};
</script>

<style lang="scss" scoped>
.config-form {
  display: flex;
  flex-direction: column;
  gap: $base-space;
  padding: $base-space * 2;
  height: 100%;
  max-width: 1000px;
  margin: 0 auto;
  &__content {
    display: flex;
    justify-content: center;
    gap: $base-space * 2;
    min-height: 0;
  }
  &__col-wrapper {
    position: relative;
    width: 100%;
    max-width: 440px;
  }
  &__col {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--bg-accent-grey-1);
    border: 1px solid var(--bg-opacity-6);
    border-radius: $border-radius-m;
    &__header {
      display: flex;
      justify-content: space-between;
      min-height: $base-space * 6;
      align-items: center;
      padding: $base-space $base-space * 2;
      font-weight: 500;
    }
    &__content {
      display: flex;
      flex-direction: column;
      padding: $base-space $base-space * 2 $base-space * 2;
      gap: $base-space;
      overflow: auto;
      height: 100%;
      &.--questions {
        padding-bottom: $base-space * 9;
      }
    }
  }
  &__draggable-area {
    display: flex;
    flex-direction: column;
    gap: $base-space;
  }
  &__selector {
    &__intro {
      display: block;
      padding: 4px;
      background: var(--bg-congig-alert);
      @include font-size(12px);
      @include line-height(16px);
    }
  }
  &__subset {
    display: flex;
    gap: $base-space;
    align-items: center;
    font-weight: 400;
  }
  &__button-area {
    display: flex;
    justify-content: right;
    position: absolute;
    bottom: 1px;
    right: 1px;
    left: 1px;
    background: var(--bg-accent-grey-1);
    padding: $base-space * 2;
    border-radius: $border-radius-m;
  }
}
</style>
