<template>
  <BaseLoading v-if="$fetchState.pending" />
  <RecordFeedbackTaskAndQuestionnaireContent
    v-else-if="!$fetchState.pending"
    :datasetId="datasetId"
    :recordOffset="currentPage"
    :key="currentPage"
  />
</template>

<script>
import { isNil } from "lodash";
import { updateTotalRecordsByDatasetId } from "@/models/feedback-task-model/feedback-dataset/feedbackDataset.queries";
import { upsertDatasetQuestions } from "@/models/feedback-task-model/dataset-question/datasetQuestion.queries";
import {
  upsertRecords,
  getRecordWithFieldsByDatasetId,
} from "@/models/feedback-task-model/record/record.queries";
import {
  COMPONENT_TYPE,
  CORRESPONDING_COMPONENT_TYPE_FROM_API,
} from "@/components/feedback-task/feedbackTask.properties";

const TYPE_OF_FEEDBACK = Object.freeze({
  ERROR_FETCHING_RECORDS: "ERROR_FETCHING_RECORDS",
  ERROR_FETCHING_QUESTIONS: "ERROR_FETCHING_QUESTIONS",
});

export default {
  name: "CenterFeedbackTaskContent",
  props: {
    datasetId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      currentPage: 0,
    };
  },
  async fetch() {
    // FETCH questions by dataset
    const { items: questions } = await this.getQuestions(this.datasetId);

    // FORMAT questions to have the shape of ORM
    const formattedQuestionsForOrm = this.factoryQuestionsForOrm(questions);

    // UPSERT formatted questions in ORM
    upsertDatasetQuestions(formattedQuestionsForOrm);

    this.onBusEventCurrentPage();
  },
  watch: {
    currentPage: {
      immediate: true,

      async handler(newCurrentPage) {
        const isDataForNextPage = isNil(
          getRecordWithFieldsByDatasetId(this.datasetId, newCurrentPage)
        );

        if (isDataForNextPage) {
          const { items: records, total: totalRecords } = await this.getRecords(
            this.datasetId,
            newCurrentPage
          );

          const formattedRecords = this.factoryRecordsForOrm(
            records,
            newCurrentPage
          );

          updateTotalRecordsByDatasetId(this.datasetId, totalRecords);
          upsertRecords(formattedRecords);
        }
      },
    },
  },
  methods: {
    onBusEventCurrentPage() {
      this.$root.$on("current-page", (currentPage) => {
        //NOTE - the pagination start at 1 but the record start at 1 => there is an offset of 1 to remove
        this.currentPage = currentPage - 1;
      });
    },
    factoryRecordsForOrm(records, offset = 0) {
      return records.map((record, index) => {
        const recordId = record.id ?? `record_${index}`;
        const recordFields = this.factoryRecordFieldsForOrm(
          record.fields,
          recordId
        );

        const recordResponses = this.factoryRecordResponsesForOrm(
          record.response?.values ?? {},
          recordId
        );

        return {
          ...record,
          record_id: recordId,
          record_index: index + offset,
          dataset_id: this.datasetId,
          record_status: record.recordStatus ?? null,
          record_fields: recordFields,
          record_responses: recordResponses,
        };
      });
    },
    factoryQuestionsForOrm(initialQuestions) {
      return initialQuestions.map(
        (
          {
            id: questionId,
            name: questionName,
            title: questionTitle,
            required: isRequired,
            settings: questionSettings,
          },
          index
        ) => {
          const componentTypeFromBack = questionSettings.type.toLowerCase();
          const componentType =
            CORRESPONDING_COMPONENT_TYPE_FROM_API[componentTypeFromBack];

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
            tooltip_message: questionSettings?.tooltip ?? null,
          };
        }
      );
    },
    formatOptionsFromQuestionApi(options, prefixForIdOfOptions, componentType) {
      // NOTE - the value of the options in questions from API and the value in the DatasetQuestion ORM are different
      // - the value from the options from the questions in API could be anything (string, number, etc.)
      // - the value from the options in the DatasetQuestion ORM is a boolean, it the state of the 'checkbox  true (if selected) or false (not selected)
      // => this is why value is initiate as false for RATING and "" for FREE_TEXT

      let defaultValueByComponent = null;

      switch (componentType.toUpperCase()) {
        case COMPONENT_TYPE.FREE_TEXT:
          defaultValueByComponent = false;
          break;
        case COMPONENT_TYPE.RATING:
          defaultValueByComponent = "";
          break;
        default:
          console.log(`the component type ${componentType} is unknown`);
      }

      return (
        options?.map((option, index) => {
          const optionText = option.text ?? option.value;
          const paramObject = {
            index,
            value: defaultValueByComponent,
            text: optionText,
            prefixForIdOfOptions,
          };

          return this.factoryOption(paramObject);
        }) ?? [this.factoryOption({ prefixForIdOfOptions })]
      );
    },
    factoryOption({
      index = 0,
      value = null,
      text = "",
      prefixForIdOfOptions,
    }) {
      return {
        id: `${prefixForIdOfOptions}_${index}`,
        value,
        text,
      };
    },
    factoryRecordFieldsForOrm(fieldsObj, recordId) {
      const fields = Object.entries(fieldsObj).map(
        ([fieldKey, fieldValue], index) => {
          return {
            id: `${recordId}_${index}`,
            title: fieldKey,
            text: fieldValue,
          };
        }
      );
      return fields;
    },
    factoryRecordResponsesForOrm(
      responsesByQuestions,
      recordId,
      userId = null
    ) {
      const responses = Object.entries(responsesByQuestions).map(
        ([questionId, responseValues]) => {
          const newOptions = Array.isArray(responseValues)
            ? responseValues
            : [responseValues];

          const formattedOptions = newOptions.map((option, index) =>
            this.factoryOption({
              index,
              value: option.value,
              text: option.value,
              prefixForIdOfOptions: questionId,
            })
          );

          return {
            question_id: questionId,
            record_id: recordId,
            options: formattedOptions,
            user_id: userId,
          };
        }
      );

      return responses;
    },
    async getRecords(datasetId, currentPage, numberOfRecordsToFetch = 5) {
      try {
        const { data } = await this.$axios.get(
          `/v1/datasets/${datasetId}/records?include=responses&offset=${currentPage}&limit=${numberOfRecordsToFetch}`
        );

        return data;
      } catch (err) {
        throw {
          response: TYPE_OF_FEEDBACK.ERROR_FETCHING_RECORDS,
        };
      }
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
  },
  destroyed() {
    this.$root.$off("current-page");
  },
};
</script>
