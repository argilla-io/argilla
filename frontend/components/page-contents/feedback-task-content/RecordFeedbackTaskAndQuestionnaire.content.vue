<template>
  <!-- <div class="wrapper">
    <RecordFeedbackTaskComponent v-if="record" :record="record" />
    <QuestionsFormComponent
      v-if="questionsWithRecordAnswers && questionsWithRecordAnswers.length"
      :initialInputs="questionsWithRecordAnswers"
    />
  </div> -->
  <div class="">{{ recordOffset }}</div>
</template>

<script>
import {
  getQuestionsByDatasetId,
  getComponentTypeOfQuestionByDatasetIdAndQuestionName,
  getOptionsOfQuestionByDatasetIdAndQuestionName,
} from "@/models/feedback-task-model/dataset-question/datasetQuestion.queries";
import {
  upsertRecords,
  getRecordWithFieldsByDatasetId,
  isRecordWithRecordIndexByDatasetIdExists,
} from "@/models/feedback-task-model/record/record.queries";
import {
  upsertRecordResponses,
  getRecordResponsesByRecordId,
} from "@/models/feedback-task-model/record-response/recordResponse.queries";
import {
  updateTotalRecordsByDatasetId,
  getTotalRecordByDatasetId,
} from "@/models/feedback-task-model/feedback-dataset/feedbackDataset.queries";
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
      return getRecordWithFieldsByDatasetId(this.datasetId, this.recordOffset);
    },
    questions() {
      return getQuestionsByDatasetId(
        this.datasetId,
        this.orderBy?.orderQuestionsBy,
        this.orderBy?.ascendent
      );
    },
    // recordResponses() {
    //   if (this.record && this.userId)
    //     return getRecordResponsesByRecordId({
    //       userId: this.userId,
    //       recordId: this.record.id,
    //     });
    // },
    // questionsWithRecordAnswers() {
    //   if (this.record) {
    //     const newOptionsByQuestion = this.factoryNewOptionsByQuestion();
    //     return this.factoryQuestionsWithRecordAnswer(newOptionsByQuestion);
    //   }
    // },
  },
  // mounted() {
  //   if (this.record) {
  //     const newOptionsByQuestion = this.factoryNewOptionsByQuestion();
  //     console.log("daboudi", newOptionsByQuestion);
  //     console.log(
  //       "dabouda",
  //       this.factoryQuestionsWithRecordAnswer(newOptionsByQuestion)
  //     );
  //   }
  // },
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
        2
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
                  case "RATING":
                    // NOTE - the 'value' of the recordResponseByQuestionName is the text of the optionsByQuestionName
                    formattedOptionsWithRecordResponse =
                      optionsByQuestionName.map(({ id, text, value }) => {
                        if (text === recordResponseByQuestionName.value) {
                          return {
                            id,
                            text,
                            value: true,
                          };
                        }
                        return { id, text, value };
                      });
                    break;
                  case "FREE_TEXT":
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
    // factoryQuestionsWithRecordAnswer(newOptionsByQuestion) {
    //   const questionsWithRecordAnswers = this.questions.map((question) => {
    //     console.log(question);
    //     const newOptions =
    //       newOptionsByQuestion.find(
    //         (recordResponseByQuestion) =>
    //           recordResponseByQuestion.question_name === question.name
    //       )?.newOptions || question.options;
    //     return { ...question, options: newOptions };
    //   });
    //   return questionsWithRecordAnswers;
    // },
    // factoryNewOptionsByQuestion() {
    //   const newOptionsByQuestion = [];
    //   this.questions.forEach((question) => {
    //     this.recordResponses.forEach((response) => {
    //       if (response.question_name === question.name) {
    //         const newOptions = question.options.map((output) => {
    //           const recordResponseOutputWithSameTextAsInQuestionOutput =
    //             response.options.find(
    //               (responseOutput) => responseOutput.id === output.id
    //             );
    //           if (recordResponseOutputWithSameTextAsInQuestionOutput) {
    //             console.log(
    //               "ici",
    //               recordResponseOutputWithSameTextAsInQuestionOutput
    //             );
    //             return {
    //               id: recordResponseOutputWithSameTextAsInQuestionOutput.id,
    //               value: true,
    //               text: output.text,
    //             };
    //           }
    //           return output;
    //         });
    //         newOptionsByQuestion.push({
    //           question_name: question.name,
    //           newOptions,
    //         });
    //       }
    //     });
    //   });
    //   return newOptionsByQuestion;
    // },
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
