<template>
  <div
    v-if="!$fetchState.pending && !$fetchState.error"
    :key="recordOffset"
    class="wrapper"
  >
    <transition
      :name="transitionWhenNavigating && 'record-page'"
      v-if="recordId"
      appear
    >
      <div class="content">
        <RecordFeedbackTaskComponent
          v-if="fieldsWithRecordFieldText"
          :recordStatus="record.record_status"
          :fields="fieldsWithRecordFieldText"
        />
        <QuestionsFormComponent
          class="question-form"
          :class="statusClass"
          v-if="questionsWithRecordAnswers && questionsWithRecordAnswers.length"
          :datasetId="datasetId"
          :recordId="recordId"
          :recordStatus="record.record_status"
          :initialInputs="questionsWithRecordAnswers"
        />
      </div>
    </transition>
    <div v-else class="wrapper--empty">
      <p
        v-if="!totalRecords"
        class="wrapper__text --heading3"
        v-text="noRecordsMessage"
      />
      <BaseSpinner v-else />
    </div>
  </div>
</template>

<script>
import {
  getQuestionsByDatasetId,
  getComponentTypeOfQuestionByDatasetIdAndQuestionName,
  getOptionsOfQuestionByDatasetIdAndQuestionName,
} from "@/models/feedback-task-model/dataset-question/datasetQuestion.queries";
import { getFieldsByDatasetId } from "@/models/feedback-task-model/dataset-field/datasetField.queries";
import {
  RECORD_STATUS,
  RESPONSE_STATUS_FOR_API,
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
    recordStatusToFilterWith: {
      type: String,
      required: true,
    },
    orderQuestions: {
      type: Object,
      default: () => {
        return { orderQuestionsBy: "order", ascendent: true };
      },
    },
    orderFields: {
      type: Object,
      default: () => {
        return { orderFieldsBy: "order", ascendent: true };
      },
    },
    recordOffset: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      rerenderQuestionnaire: 1,
      transitionWhenNavigating: true,
    };
  },
  computed: {
    userId() {
      return this.$auth.user.id;
    },
    recordStatusFilterValueForGetRecords() {
      // NOTE - this is only used to fetch record, this is why the return value is in lowercase
      let paramForUrl = null;
      switch (this.recordStatusToFilterWith.toUpperCase()) {
        case RECORD_STATUS.PENDING:
          paramForUrl = RESPONSE_STATUS_FOR_API.MISSING;
          break;
        case RECORD_STATUS.SUBMITTED:
          paramForUrl = RESPONSE_STATUS_FOR_API.SUBMITTED;
          break;
        case RECORD_STATUS.DISCARDED:
          paramForUrl = RESPONSE_STATUS_FOR_API.DISCARDED;
          break;
        default:
          // NOTE - by default, records with missing responses are fetched
          paramForUrl = RESPONSE_STATUS_FOR_API.MISSING;
      }
      return paramForUrl;
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
    recordId() {
      return this.record?.id;
    },
    questions() {
      return getQuestionsByDatasetId(
        this.datasetId,
        this.orderQuestions?.orderQuestionsBy,
        this.orderQuestions?.ascendent
      );
    },
    fields() {
      return getFieldsByDatasetId(
        this.datasetId,
        this.orderFields?.orderFieldsBy,
        this.orderFields?.ascendent
      );
    },
    recordResponsesFromCurrentUser() {
      return this.record?.record_responses ?? [];
    },
    recordFields() {
      return this.record?.record_fields ?? [];
    },
    questionsWithRecordAnswers() {
      return this.questions?.map((question) => {
        const correspondingResponseToQuestion =
          this.recordResponsesFromCurrentUser.find(
            (recordResponse) => question.name === recordResponse.question_name
          );
        if (correspondingResponseToQuestion) {
          return {
            ...question,
            response_id: correspondingResponseToQuestion.id,
            options: correspondingResponseToQuestion.options,
          };
        }
        return { ...question, response_id: null };
      });
    },
    fieldsWithRecordFieldText() {
      return this.fields?.map((field) => {
        const correspondingRecordFieldToField = this.recordFields.find(
          (recordField) => field.name === recordField.field_name
        );

        if (correspondingRecordFieldToField) {
          return {
            ...field,
            field_text: correspondingRecordFieldToField.text,
          };
        }
      });
    },
    noRecordsMessage() {
      return `There are no ${this.recordStatusToFilterWith} records`;
    },
    statusClass() {
      return `--${this.record.record_status.toLowerCase()}`;
    },
  },
  async fetch() {
    await this.initRecordsInDatabase(this.recordOffset);
  },
  watch: {
    recordOffset(newRecordOffset) {
      const isRecordWithRecordOffsetNotExists =
        !isRecordWithRecordIndexByDatasetIdExists(
          this.datasetId,
          newRecordOffset
        );
      if (isRecordWithRecordOffsetNotExists) {
        this.initRecordsInDatabase(newRecordOffset);
      }
    },
  },
  methods: {
    async initRecordsInDatabase(recordOffset) {
      // FETCH records from recordOffset + 5 next records
      const { items: records, total: totalRecords } = await this.getRecords(
        this.datasetId,
        recordOffset,
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
        const url = `/v1/me/datasets/${datasetId}/records?include=responses&offset=${recordOffset}&limit=${numberOfRecordsToFetch}&response_status=${this.recordStatusFilterValueForGetRecords}`;
        const { data } = await this.$axios.get(url);
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
          { id: recordId, responses: recordResponses, fields: recordFields },
          index
        ) => {
          const formattedRecordFields = this.factoryRecordFieldsForOrm(
            recordFields,
            recordId
          );

          // NOTE - the record status come from the corresponding responses
          const { formattedRecordResponsesForOrm, recordStatus } =
            this.factoryRecordResponsesForOrm({ recordId, recordResponses });

          return {
            id: recordId,
            record_index: index + this.recordOffset,
            dataset_id: this.datasetId,
            record_status: recordStatus ?? RECORD_STATUS.PENDING,
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
            field_name: fieldKey,
            text: fieldValue,
          };
        }
      );
      return fields;
    },
    factoryRecordResponsesForOrm({ recordId, recordResponses }) {
      const formattedRecordResponsesForOrm = [];
      // NOTE - by default, recordStatus is at "PENDING"
      let recordStatus = RECORD_STATUS.PENDING;
      recordResponses.forEach((responsesByRecordAndUser) => {
        recordStatus = responsesByRecordAndUser.status ?? RECORD_STATUS.PENDING;
        if (responsesByRecordAndUser.values) {
          if (Object.keys(responsesByRecordAndUser.values).length === 0) {
            // IF responses.value  is an empty object, init formatted responses with questions data
            this.questions.forEach(
              ({ name: questionName, options: questionOptions }) => {
                formattedRecordResponsesForOrm.push({
                  id: responsesByRecordAndUser.id,
                  question_name: questionName,
                  options: questionOptions,
                  record_id: recordId,
                  user_id: responsesByRecordAndUser.user_id ?? null,
                });
              }
            );
          } else {
            // ELSE responses.value is not an empty object, init formatted responses with questions data and corresponding responses
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
                  case COMPONENT_TYPE.SINGLE_LABEL:
                  case COMPONENT_TYPE.RATING:
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
          }
        }
      });

      return { formattedRecordResponsesForOrm, recordStatus };
    },
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-wrap: wrap;
  height: 100%;
  &__text {
    color: $black-54;
  }
  &--empty {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
.content {
  display: flex;
  flex: 1;
  flex-wrap: wrap;
  gap: 2 * $base-space;
  height: 100%;
}
.question-form {
  border: 1px solid transparent;
  &.--pending {
    border-color: transparent;
  }
  &.--discarded {
    border-color: #c3c3c3;
  }
  &.--submitted {
    border-color: $primary-color;
  }
}

.record-page-enter-active,
.record-page-leave-active {
  transition: all 1s;
}
.record-page-enter,
.record-page-leave-to {
  opacity: 0;
}
</style>
