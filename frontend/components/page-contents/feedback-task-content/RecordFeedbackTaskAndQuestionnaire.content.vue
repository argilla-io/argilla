<template>
  <div class="wrapper" v-if="!$fetchState.pending && !$fetchState.error">
    <RecordFeedbackTaskComponent v-if="record" :record="record" />
    <QuestionsFormComponent
      :key="recordOffset"
      v-if="questionsWithRecordAnswers && questionsWithRecordAnswers.length"
      :initialInputs="questionsWithRecordAnswers"
    />
  </div>
</template>

<script>
import {
  getQuestionsByDatasetId,
  getComponentTypeOfQuestionByDatasetIdAndQuestionName,
  getOptionsOfQuestionByDatasetIdAndQuestionName,
} from "@/models/feedback-task-model/dataset-question/datasetQuestion.queries";
import {
  upsertRecords,
  getRecordWithFieldsAndResponsesByUserId,
  isRecordWithRecordIndexByDatasetIdExists,
} from "@/models/feedback-task-model/record/record.queries";
import {
  updateTotalRecordsByDatasetId,
  getTotalRecordByDatasetId,
} from "@/models/feedback-task-model/feedback-dataset/feedbackDataset.queries";
import { COMPONENT_TYPE } from "@/components/feedback-task/feedbackTask.properties";

const TYPE_OF_FEEDBACK = Object.freeze({
  ERROR_FETCHING_RECORDS: "ERROR_FETCHING_RECORDS",
});

export default {
  name: "RecordFeedbackTaskAndQuestionnaireComponent",
  props: {
    datasetId: {
      type: String,
      required: true,
    },
    orderBy: {
      type: Object,
      default: () => {
        return { orderQuestionBy: "order", ascendent: true };
      },
    },
    recordOffset: {
      type: Number,
      required: true,
    },
  },
  computed: {
    userId() {
      return this.$auth.user.id;
    },
    totalRecords() {
      return getTotalRecordByDatasetId(this.datasetId);
    },
    record() {
      return getRecordWithFieldsAndResponsesByUserId(
        this.datasetId,
        this.userId,
        this.recordOffset
      );
    },
    questions() {
      return getQuestionsByDatasetId(
        this.datasetId,
        this.orderBy?.orderQuestionsBy,
        this.orderBy?.ascendent
      );
    },
    recordResponsesFromCurrentUser() {
      return this.record?.record_responses ?? [];
    },
    questionsWithRecordAnswers() {
      return this.questions?.map((question) => {
        const correspondingResponseOptionsToQuestion =
          this.recordResponsesFromCurrentUser.find(
            (recordResponse) => question.name === recordResponse.question_name
          )?.options;
        if (correspondingResponseOptionsToQuestion)
          return {
            ...question,
            options: correspondingResponseOptionsToQuestion,
          };
        return { ...question };
      });
    },
  },
  async fetch() {
    await this.initRecordsInDatabase();
  },
  watch: {
    recordOffset(newRecordOffset) {
      const isRecordWithRecordOffsetNotExists =
        !isRecordWithRecordIndexByDatasetIdExists(
          this.datasetId,
          newRecordOffset
        );
      if (
        newRecordOffset < this.totalRecords &&
        isRecordWithRecordOffsetNotExists
      ) {
        this.initRecordsInDatabase();
      }
    },
  },
  methods: {
    async initRecordsInDatabase() {
      // FETCH records from recordOffset + 5 next records
      const { items: records, total: totalRecords } = await this.getRecords(
        this.datasetId,
        this.recordOffset,
        5
      );

      // FORMAT records for orm
      const formattedRecords = this.factoryRecordsForOrm(records);

      // UPSERT total records && records in ORM
      updateTotalRecordsByDatasetId(this.datasetId, totalRecords);
      upsertRecords(formattedRecords);
    },
    async getRecords(datasetId, recordOffset, numberOfRecordsToFetch = 5) {
      try {
        const { data } = await this.$axios.get(
          `/v1/datasets/${datasetId}/records?include=responses&offset=${recordOffset}&limit=${numberOfRecordsToFetch}`
        );
        return data;
      } catch (err) {
        throw {
          response: TYPE_OF_FEEDBACK.ERROR_FETCHING_RECORDS,
        };
      }
    },
    factoryRecordsForOrm(records) {
      return records.map(
        (
          {
            id: recordId,
            responses: recordResponses,
            fields: recordFields,
            recordStatus,
          },
          index
        ) => {
          const formattedRecordFields = this.factoryRecordFieldsForOrm(
            recordFields,
            recordId
          );

          const formattedRecordResponsesForOrm =
            this.factoryRecordResponsesForOrm({ recordId, recordResponses });

          return {
            id: recordId,
            record_index: index + this.recordOffset,
            dataset_id: this.datasetId,
            record_status: recordStatus ?? null,
            record_fields: formattedRecordFields,
            record_responses: formattedRecordResponsesForOrm,
          };
        }
      );
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
    factoryRecordResponsesForOrm({ recordId, recordResponses }) {
      const formattedRecordResponsesForOrm = [];
      recordResponses.forEach((responsesByRecordAndUser) => {
        Object.entries(responsesByRecordAndUser.values).forEach(
          ([questionName, recordResponseByQuestionName]) => {
            let formattedOptionsWithRecordResponse = [];

            const optionsByQuestionName =
              getOptionsOfQuestionByDatasetIdAndQuestionName(
                this.datasetId,
                questionName
              );
            const correspondingComponentTypeOfTheAnswer =
              getComponentTypeOfQuestionByDatasetIdAndQuestionName(
                this.datasetId,
                questionName
              );

            switch (correspondingComponentTypeOfTheAnswer) {
              case COMPONENT_TYPE.RATING:
                // NOTE - the 'value' of the recordResponseByQuestionName is the text of the optionsByQuestionName
                formattedOptionsWithRecordResponse = optionsByQuestionName.map(
                  ({ id, text, value }) => {
                    if (text === recordResponseByQuestionName.value) {
                      return {
                        id,
                        text,
                        value: true,
                      };
                    }
                    return { id, text, value };
                  }
                );
                break;
              case COMPONENT_TYPE.FREE_TEXT:
                formattedOptionsWithRecordResponse = [
                  {
                    id: questionName,
                    text: recordResponseByQuestionName.value,
                    value: recordResponseByQuestionName.value,
                  },
                ];
                break;
              default:
                console.log(
                  `The corresponding component with a question name:'${questionName}' was not found`
                );
            }
            formattedRecordResponsesForOrm.push({
              id: responsesByRecordAndUser.id,
              question_name: questionName,
              options: formattedOptionsWithRecordResponse,
              record_id: recordId,
              user_id: responsesByRecordAndUser.user_id ?? null,
            });
          }
        );
      });

      return formattedRecordResponsesForOrm;
    },
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 2 * $base-space;
}
</style>
