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
    const questions = await this.getQuestions(this.datasetId);

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
          getRecordWithFieldsByDatasetId(this.datasetId, 1, newCurrentPage)
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
        const recordFields = this.factoryRecordFieldsForOrm(record.fields);

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
          const componentType = this.factoryComponentType(
            questionSettings.type
          );

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
        case "FREE_TEXT":
          defaultValueByComponent = false;
          break;
        case "RATING":
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
    factoryComponentType(componentType) {
      // Here we translate the name from back to the corresponding component in front
      let frontComponentType = null;

      switch (componentType.toUpperCase()) {
        case "TEXT":
          frontComponentType = "FREE_TEXT";
          break;
        case "RATING":
          frontComponentType = "RATING";
          break;
        default:
          console.log(`the component type ${componentType} is unknown`);
      }

      return frontComponentType;
    },
    factoryRecordFieldsForOrm(fieldsObj) {
      const fields = Object.entries(fieldsObj).map(
        ([fieldKey, fieldValues]) => {
          return { name: fieldKey, ...fieldValues };
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

        // FIXME - next two lines (data.items = ... and data.total = ...) are temporary until we received the list of records from back
        data.items = [
          {
            id: "record_0",
            fields: {
              field_1: {
                title: "Input",
                text: "Lorem ipsum dolor sit amet consectetur adipisicing elit. Dolorum ratione quas quis eveniet harum cum, earum a facere voluptate fugit nostrum sequi facilis incidunt debitis unde? Eos rem debitis velit? Officia magni odit possimus quis nisi. Dolore, eaque eligendi! Beatae quos debitis soluta distinctio qui ex sint nesciunt non quidem laboriosam. Veniam ex accusantium explicabo ab, pariatur id sapiente tenetur. ",
              },
              field_2: {
                title: "Output",
                text: "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Vitae cupiditate fugit quos officiis expedita, deleniti libero inventore fugiat perferendis dolor optio praesentium enim molestiae molestias. Ipsam perferendis aperiam perspiciatis assumenda. Numquam reprehenderit non distinctio repellat adipisci laborum, fugit sint labore nulla tempore quam eos iste asperiores eius laudantium vel similique officiis sunt vero beatae magni ab dicta! Culpa, qui dolore. Quaerat, repellendus deserunt doloribus laudantium ducimus atque quia rerum ullam. Sit veritatis, quas id sed culpa deleniti officiis ipsa laudantium, eos qui pariatur iure facere, sequi delectus similique! Commodi, a. Totam illo iure iste voluptate? Veritatis blanditiis est rem? Ipsam consequatur incidunt obcaecati distinctio qui beatae quaerat, ullam sit voluptas facere repellat accusamus dolorem iure aliquam fugit veritatis nesciunt modi. Dolore corrupti assumenda tenetur soluta et? Laborum nemo repellendus architecto necessitatibus accusamus nesciunt exercitationem neque dicta! Dolore sed atque nam sit ea earum quia minima, veniam natus non hic necessitatibus. Quibusdam repudiandae odit eaque enim voluptatem fugiat hic quidem voluptate, sint id quae a? Perferendis ad suscipit reiciendis dolor omnis corrupti quos porro aliquid recusandae. Ipsam doloribus esse debitis libero. Quod corporis eveniet cupiditate aliquid, iure sed dignissimos repellat architecto quaerat impedit animi porro saepe ipsa molestiae quibusdam suscipit nam. Fuga quo sunt itaque corrupti atque dolores fugit, eligendi voluptate.",
              },
            },
            external_id: "string",
            response: {
              values: {
                "question-01": {
                  value: 2,
                },
                comment: {
                  value: "I'm blue daboudi dabouda",
                },
              },
            },
          },
          {
            id: "record_1",
            fields: {
              field_1: {
                title: "Input",
                text: "Lorem ipsum dolor sit amet consectetur adipisicing elit. Dolorum ratione quas quis eveniet harum cum, earum a facere voluptate fugit nostrum sequi facilis incidunt debitis unde? Eos rem debitis velit? Officia magni odit possimus quis nisi. Dolore, eaque eligendi! Beatae quos debitis soluta distinctio qui ex sint nesciunt non quidem laboriosam. Veniam ex accusantium explicabo ab, pariatur id sapiente tenetur. ",
              },
            },
            external_id: "string",
            response: {
              values: {
                "question-01": {
                  value: 2,
                },
                comment: {
                  value: "I'm blue daboudi dabouda",
                },
              },
            },
          },
        ];

        data.total = data.items.length;

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
          `/v1/datasets/${datasetId}/annotations`
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
