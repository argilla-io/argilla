<template>
  <RecordFeedbackTaskAndQuestionnaireContent
    :datasetId="datasetId"
    :recordOffset="currentPage"
    :key="currentPage"
  />
</template>

<script>
import { isNil } from "lodash";
import { upsertDatasetQuestions } from "@/models/feedback-task-model/dataset-question/datasetQuestion.queries";
import {
  upsertRecords,
  getRecordWithFieldsByDatasetId,
} from "@/models/feedback-task-model/record/record.queries";

const TYPE_OF_FEEDBACK = Object.freeze({
  ERROR_FETCHING_RECORDS: "ERROR_FETCHING_RECORDS",
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
  async created() {
    // TODO - INITIAL inputs, will be replaced by API values
    const inputs = [
      // {
      //   id: "id_1",
      //   question:
      //     "Are the instruction and input adequate for the capabilities of this model?",
      //   options: [
      //     { id: 1, value: true, text: "Yes" },
      //     { id: 2, value: false, text: "No" },
      //   ],
      //   default: null,
      //   required: true,
      //   componentType: "SINGLE_LABEL",
      //   tooltipMessage: null,
      // },
      {
        id: "id_5",
        name: "nameOfQuestion_id_5",
        question:
          "Rate the helpfulness of the output (1-not helpful, 7-very helpful):",
        options: [
          { id: 1, value: false, text: "1" },
          { id: 2, value: false, text: "2" },
          { id: 3, value: false, text: "3" },
          { id: 4, value: false, text: "4" },
          { id: 5, value: false, text: "5" },
          { id: 6, value: false, text: "6" },
          { id: 7, value: false, text: "7" },
        ],
        required: true,
        componentType: "RATING",
      },
      {
        id: "id_6",
        name: "nameOfQuestion_id_6",
        question:
          "Rate the harmlessness of the output (1-very harmful, 5-harmless):",
        options: [
          { id: "id_6-1", value: false, text: "1" },
          { id: "id_6-2", value: false, text: "2" },
          { id: "id_6-3", value: false, text: "3" },
          { id: "id_6-4", value: false, text: "4" },
          { id: "id_6-5", value: false, text: "5" },
        ],
        required: false,
        tooltipMessage: "This is a tooltipz",
        componentType: "RATING",
      },
      {
        id: "id_7",
        name: "nameOfQuestion_id_7",
        question: "Comment",
        placeholder: "this is the placeholder",
        options: [
          {
            id: "id_text_area_option",
            text: "",
            value: "",
          },
        ],
        default: null,
        required: true,
        tooltipMessage: "This is a tooltip",
        componentType: "FREE_TEXT",
      },
    ];

    // FORMAT questions in good orm shapes
    const formattedQuestions = this.factoryQuestionsForOrm(inputs);

    // UPSERT records and questions in ORM
    upsertDatasetQuestions(formattedQuestions);

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
          const records = await this.getRecords(this.datasetId, newCurrentPage);
          const formattedRecords = this.factoryRecordsForOrm(
            records,
            newCurrentPage
          );
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
        return {
          ...record,
          record_id: record.id,
          record_index: index + offset,
          dataset_id: this.datasetId,
          record_status: record.recordStatus,
          record_fields: record.fields,
          record_responses: record.responses,
        };
      });
    },
    factoryQuestionsForOrm(initialQuestions) {
      return initialQuestions.map((question, index) => {
        return {
          ...question,
          dataset_id: this.datasetId,
          order: index,
          component_type: question.componentType,
          is_required: question.required,
          tooltip_message: question.tooltipMessage,
        };
      });
    },
    async getRecords(datasetId, currentPage, numberOfRecordsToFetch = 5) {
      try {
        // TODO - replace call to api to get record with response and field
        const response = await fetch(
          `http://localhost:8000/records?_start=${currentPage}&_limit=${numberOfRecordsToFetch}`
        );
        const record = await response.json();

        return record;
      } catch (err) {
        throw {
          response: TYPE_OF_FEEDBACK.ERROR_FETCHING_RECORDS,
        };
      }
    },
  },
  destroyed() {
    this.$root.$off("current-page");
  },
};
</script>
