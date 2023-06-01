<template>
  <BaseLoading v-if="$fetchState.pending" />
  <RecordFeedbackTaskAndQuestionnaireContent v-else :datasetId="datasetId" />
</template>

<script>
import { upsertDatasetQuestions } from "@/models/feedback-task-model/dataset-question/datasetQuestion.queries";
import { upsertDatasetFields } from "@/models/feedback-task-model/dataset-field/datasetField.queries";
import {
  CORRESPONDING_QUESTION_COMPONENT_TYPE_FROM_API,
  CORRESPONDING_FIELD_COMPONENT_TYPE_FROM_API,
} from "@/components/feedback-task/feedbackTask.properties";

const TYPE_OF_FEEDBACK = Object.freeze({
  ERROR_FETCHING_QUESTIONS: "ERROR_FETCHING_QUESTIONS",
  ERROR_FETCHING_FIELDS: "ERROR_FETCHING_FIELDS",
});

export default {
  name: "CenterFeedbackTaskContent",
  props: {
    datasetId: {
      type: String,
      required: true,
    },
  },
  async fetch() {
    // FETCH questions AND fields by dataset
    const { items: questions } = await this.getQuestions(this.datasetId);
    const { items: fields } = await this.getFields(this.datasetId);

    // FORMAT questions AND fields to have the shape of ORM
    const formattedQuestionsForOrm = this.factoryQuestionsForOrm(questions);
    const formattedFieldsForOrm = this.factoryFieldsForOrm(fields);

    // UPSERT formatted questions in ORM
    await upsertDatasetQuestions(formattedQuestionsForOrm);
    await upsertDatasetFields(formattedFieldsForOrm);
  },

  methods: {
    factoryQuestionsForOrm(initialQuestions) {
      return initialQuestions.map(
        (
          {
            id: questionId,
            name: questionName,
            title: questionTitle,
            required: isRequired,
            settings: questionSettings,
            description: questionDescription,
          },
          index
        ) => {
          const componentTypeFromBack = questionSettings.type.toLowerCase();
          const componentType =
            CORRESPONDING_QUESTION_COMPONENT_TYPE_FROM_API[
              componentTypeFromBack
            ];

          const formattedOptions = this.formatOptionsFromQuestionApi(
            questionSettings.options,
            questionName,
            componentType
          );

          return {
            id: questionId,
            name: questionName,
            dataset_id: this.datasetId,
            order: index,
            question: questionTitle,
            options: formattedOptions,
            is_required: isRequired,
            component_type: componentType,
            placeholder: questionSettings?.placeholder ?? null,
            description: questionDescription ?? null,
            settings: questionSettings,
          };
        }
      );
    },
    factoryFieldsForOrm(initialFields) {
      return initialFields.map(
        (
          {
            id: fieldId,
            name: fieldName,
            title: fieldTitle,
            required: isRequired,
            settings: fieldSettings,
          },
          index
        ) => {
          const componentTypeFromBack =
            fieldSettings?.type?.toLowerCase() ?? null;

          const componentType = componentTypeFromBack
            ? CORRESPONDING_FIELD_COMPONENT_TYPE_FROM_API[componentTypeFromBack]
            : null;

          return {
            id: fieldId,
            name: fieldName,
            dataset_id: this.datasetId,
            order: index,
            title: fieldTitle,
            is_required: isRequired,
            component_type: componentType,
            settings: fieldSettings,
          };
        }
      );
    },
    formatOptionsFromQuestionApi(options, questionName) {
      // NOTE - the value of the options in questions from API and the value in the DatasetQuestion ORM are different
      // - the value from the options from the questions in API could be anything (string, number, etc.)
      // - the value from the options in the DatasetQuestion ORM is a boolean, it the state of the 'checkbox  true (if selected) or false (not selected)
      // => this is why value is initiate as false for RATING and "" for FREE_TEXT

      // TODO - the next logic is only for RATING && SINGLE_LABEL => put it directly in switch case
      if (options) {
        return options?.map((option) => {
          const optionText = option.text ?? option.value;
          const paramObject = {
            value: option.value,
            text: optionText,
            prefixId: questionName,
            suffixId: option.value,
          };

          return this.factoryOption(paramObject);
        });
      }

      // TODO - the next logic return is only for FREE_TEXT => put it directly in switch case
      return [
        this.factoryOption({
          value: "",
          prefixId: questionName,
        }),
      ];
    },
    factoryOption({ value = null, text = "", prefixId, suffixId }) {
      return {
        id: `${prefixId}${suffixId ? `_${suffixId}` : ""}`,
        value,
        text,
      };
    },
    async getQuestions(datasetId) {
      try {
        const { data } = await this.$axios.get(
          `/v1/datasets/${datasetId}/questions`
        );

        return data;
      } catch (err) {
        throw {
          response: TYPE_OF_FEEDBACK.ERROR_FETCHING_QUESTIONS,
        };
      }
    },
    async getFields(datasetId) {
      try {
        const { data } = await this.$axios.get(
          `/v1/datasets/${datasetId}/fields`
        );

        return data;
      } catch (err) {
        throw {
          response: TYPE_OF_FEEDBACK.ERROR_FETCHING_FIELDS,
        };
      }
    },
  },
};
</script>
