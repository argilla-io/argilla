<template>
  <section class="config-form">
    <div class="config-form__header">
      <div class="config-form__selectors">
        <DatasetConfigurationSelector
          v-if="subsets.length > 1"
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
      <div class="config-form__button-area">
        <BaseButton
          class="primary"
          @click.prevent="
            visibledatasetCreationDialog = !visibledatasetCreationDialog
          "
          >Create Dataset</BaseButton
        >
        <DatasetConfigurationDialog
          v-if="visibledatasetCreationDialog"
          :dataset-id="datasetId"
          @close-dialog="visibledatasetCreationDialog = false"
          @create-dataset="createDataset"
        />
      </div>
    </div>
    <div class="config-form__content">
      <div class="config-form__col-wrapper">
        <div class="config-form__col" v-if="selectedSubset.fields.length">
          <div class="config-form__col__header">Fields and metadata</div>
          <div class="config-form__col__content">
            <draggable
              class="config-form__draggable-area"
              :list="selectedSubset.fields"
              :group="{ name: 'fields' }"
              :disabled="isFocused"
            >
              <DatasetConfigurationField
                v-for="field in selectedSubset.fields"
                :key="field.name"
                :field="field"
                :available-field-types="availableFieldTypes"
                :available-metadata-types="availableMetadataTypes"
                @is-focused="isFocused = $event"
                @metadata-type-selected="onMetadataTypeSelected"
              />
            </draggable>
            <span
              class="config-form__separator"
              v-if="selectedSubset.metadata.length"
            />
            <draggable
              class="config-form__draggable-area"
              :list="selectedSubset.metadata"
              :group="{ name: 'metadata' }"
              :disabled="isFocused"
            >
              <DatasetConfigurationFieldMetadata
                v-for="metdataItem in selectedSubset.metadata"
                :key="metdataItem.name"
                :metadata="metdataItem"
                :available-field-types="availableFieldTypes"
                :available-metadata-types="availableMetadataTypes"
                @is-focused="isFocused = $event"
                @field-type-selected="onFieldTypeSelected"
              />
            </draggable>
          </div>
        </div>
      </div>
      <div class="config-form__col-wrapper">
        <div class="config-form__col">
          <div class="config-form__col__header">Questions</div>
          <div class="config-form__col__content">
            <draggable
              v-if="selectedSubset.questions.length"
              class="config-form__draggable-area"
              :list="selectedSubset.questions"
              :group="{ name: 'questions' }"
              :disabled="isFocused"
            >
              <DatasetConfigurationQuestion
                v-for="question in selectedSubset.questions"
                :key="question.name"
                :question="question"
                :columns="selectedSubset.columns"
                :remove-is-allowed="true"
                :available-types="availableQuestionTypes"
                @remove="selectedSubset.removeQuestion(question.name)"
                @change-type="onTypeIsChanged(question.name, $event)"
                @is-focused="isFocused = $event"
              />
            </draggable>
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
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { useDatasetConfigurationForm } from "./UseDatasetConfigurationForm";

export default {
  props: {
    subsets: {
      type: Array,
    },
    selectedSubset: {
      type: Object,
      required: true,
    },
    splits: {
      type: Array,
    },
    selectedSplit: {
      type: Object,
    },
    datasetId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      isFocused: false,
      visibledatasetCreationDialog: false,
    };
  },
  methods: {
    createDataset(name, workspace) {
      console.log("Create dataset", name, workspace);
    },
    addQuestion(type) {
      const questionName = `question_${this.selectedSubset.questions.length}`;
      this.selectedSubset.addQuestion(questionName, { type });
    },
    onMetadataTypeSelected(field) {
      this.selectedSubset.changeToMetadata(field.name, field.type.value);
    },
    onFieldTypeSelected(metadata) {
      this.selectedSubset.changeToField(metadata.name, metadata.type.value);
    },
    onTypeIsChanged(name, type) {
      this.selectedSubset.addQuestion(name, {
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
  padding: $base-space $base-space * 2 $base-space * 2 $base-space * 2;
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
    justify-content: space-evenly;
    gap: $base-space * 2;
    min-height: 0;
  }
  &__col-wrapper {
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
  &__separator {
    border-bottom: 1px solid var(--bg-opacity-10);
    margin: $base-space 0;
  }
  &__draggable-area {
    display: flex;
    flex-direction: column;
    gap: $base-space;
  }
  &__button-area {
    position: relative;
  }
}
</style>
