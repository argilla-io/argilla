<template>
  <div v-if="!$fetchState.pending && !$fetchState.error" class="wrapper">
    <template v-if="recordId">
      <RecordFeedbackTaskComponent
        v-if="fieldsWithRecordFieldText"
        :recordStatus="record.record_status"
        :fields="fieldsWithRecordFieldText"
      />
      <QuestionsFormComponent
        :key="questionFormKey"
        class="question-form"
        :class="statusClass"
        v-if="questionsWithRecordAnswers && questionsWithRecordAnswers.length"
        :datasetId="datasetId"
        :recordId="recordId"
        :recordStatus="record.record_status"
        :initialInputs="questionsWithRecordAnswers"
        @on-submit-responses="onActionInResponses('SUBMIT')"
        @on-discard-responses="onActionInResponses('DISCARD')"
        @on-question-form-touched="onQuestionFormTouched"
      />
    </template>

    <div v-else class="wrapper--empty">
      <p
        v-if="!hasRecords"
        class="wrapper__text --heading3"
        v-text="noRecordsMessage"
      />
      <BaseSpinner v-else />
    </div>
  </div>
</template>

<script>
import { isNil } from "lodash";
import { Notification } from "@/models/Notifications";
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
  deleteAllRecords,
  getRecordWithFieldsAndResponsesByUserId,
  isRecordWithRecordIndexByDatasetIdExists,
  isAnyRecordByDatasetId,
} from "@/models/feedback-task-model/record/record.queries";
import { deleteRecordResponsesByUserIdAndResponseId } from "@/models/feedback-task-model/record-response/recordResponse.queries";
import { deleteAllRecordFields } from "@/models/feedback-task-model/record-field/recordField.queries";
import { COMPONENT_TYPE } from "@/components/feedback-task/feedbackTask.properties";
import { LABEL_PROPERTIES } from "../../feedback-task/feedbackTask.properties";

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
  },
  watch: {
    async currentPage(newValue) {
      await this.$router.push({
        path: this.$route.path,
        query: {
          ...this.$route.query,
          _page: newValue,
          _status: this.recordStatusToFilterWith,
        },
      });
    },
    async recordStatusToFilterWith(newValue) {
      await this.$router.push({
        path: this.$route.path,
        query: {
          ...this.$route.query,
          _status: newValue,
          _page: this.currentPage,
        },
      });
    },
  },
  data() {
    return {
      reRenderQuestionForm: 1,
      questionFormTouched: false,
      recordStatusToFilterWith: null,
      currentPage: null,
    };
  },
  computed: {
    userId() {
      return this.$auth.user.id;
    },
    noMoreDataMessage() {
      return `You've reached the end of the data for the ${this.recordStatusToFilterWith} queue.`;
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
    record() {
      return getRecordWithFieldsAndResponsesByUserId(
        this.datasetId,
        this.userId,
        this.currentPage - 1
      );
    },
    hasRecords() {
      return isAnyRecordByDatasetId(this.datasetId);
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
      return `You have no ${this.recordStatusToFilterWith} records`;
    },
    statusClass() {
      return `--${this.record.record_status.toLowerCase()}`;
    },
    questionFormKey() {
      return `${this.currentPage}-${this.reRenderQuestionForm}`;
    },
    statusFilterFromQuery() {
      return this.$route.query?._status ?? RECORD_STATUS.PENDING.toLowerCase();
    },
    pageFromQuery() {
      const { _page } = this.$route.query;
      return isNil(_page) ? 1 : +_page;
    },
  },

  async fetch() {
    await this.cleanRecordOrm();

    await this.initRecordsInDatabase(this.currentPage - 1);

    const offset = this.currentPage - 1;
    const isRecordExistForCurrentPage =
      isRecordWithRecordIndexByDatasetIdExists(this.datasetId, offset);

    if (!isRecordExistForCurrentPage) {
      await this.initRecordsInDatabase(0);
      this.currentPage = 1;
    }
  },
  async created() {
    this.recordStatusToFilterWith = this.statusFilterFromQuery;
    this.currentPage = this.pageFromQuery;
  },
  mounted() {
    this.$root.$on("go-to-next-page", () => {
      this.setCurrentPage(this.currentPage + 1);
    });
    this.$root.$on("go-to-prev-page", () => {
      this.setCurrentPage(this.currentPage - 1);
    });
    this.$root.$on("status-filter-changed", this.onStatusFilterChanged);
  },
  methods: {
    async applyStatusFilter(status) {
      this.recordStatusToFilterWith = status;
      this.currentPage = 1;

      await this.$fetch();

      this.reRenderQuestionForm++;
    },
    emitResetStatusFilter() {
      this.$root.$emit("reset-status-filter");
    },
    async onStatusFilterChanged(newStatus) {
      if (this.recordStatusToFilterWith === newStatus) {
        return;
      }

      const localApplyStatusFilter = this.applyStatusFilter;
      const localEmitResetStatusFilter = this.emitResetStatusFilter;

      if (this.questionFormTouched) {
        Notification.dispatch("notify", {
          message: "Your changes will be lost if you move to another view",
          numberOfChars: 500,
          type: "warning",
          buttonText: LABEL_PROPERTIES.CONTINUE,
          async onClick() {
            await localApplyStatusFilter(newStatus);
          },
          onClose() {
            localEmitResetStatusFilter();
          },
        });
      } else {
        await this.applyStatusFilter(newStatus);
      }
    },
    onQuestionFormTouched(isTouched) {
      this.questionFormTouched = isTouched;
    },
    async setCurrentPage(newPage) {
      const offset = newPage - 1;
      let isNextRecordExist = isRecordWithRecordIndexByDatasetIdExists(
        this.datasetId,
        offset
      );

      // if isNextRecordExist => move to the next one
      // else fetch new set of records and move to next one
      if (!isNextRecordExist) {
        await this.initRecordsInDatabase(offset);
        isNextRecordExist = isRecordWithRecordIndexByDatasetIdExists(
          this.datasetId,
          offset
        );
      }

      if (isNextRecordExist) {
        this.currentPage = newPage;
      } else if (this.currentPage < newPage) {
        // notify there is no more records
        Notification.dispatch("notify", {
          message: this.noMoreDataMessage,
          numberOfChars: this.noMoreDataMessage.length,
          type: "info",
        });
      }
    },
    async onActionInResponses(typeOfAction) {
      switch (typeOfAction) {
        case "SUBMIT":
        case "DISCARD":
          this.setCurrentPage(this.currentPage + 1);
          break;
        default:
        // do nothing
      }
    },
    async initRecordsInDatabase(
      offset,
      status = this.recordStatusFilterValueForGetRecords
    ) {
      // FETCH records from offset, status + 10 next records
      const { items: records } = await this.getRecords(
        this.datasetId,
        offset,
        status
      );
      // FORMAT records for orm
      const formattedRecords = this.factoryRecordsForOrm(records, offset);

      // UPSERT records in ORM
      await upsertRecords(formattedRecords);
    },
    async getRecords(
      datasetId,
      offset,
      responseStatus,
      numberOfRecordsToFetch = 10
    ) {
      try {
        const url = `/v1/me/datasets/${datasetId}/records`;
        const params = {
          include: "responses",
          offset,
          limit: numberOfRecordsToFetch,
          response_status: responseStatus,
        };
        const { data } = await this.$axios.get(url, { params });
        return data;
      } catch (err) {
        console.warn(err);
        throw {
          response: TYPE_OF_FEEDBACK.ERROR_FETCHING_RECORDS,
        };
      }
    },
    factoryRecordsForOrm(records, offset) {
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
            record_index: index + offset,
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
                        if (value === recordResponseByQuestionName.value) {
                          return {
                            id,
                            text,
                            value,
                            is_selected: true,
                          };
                        }
                        return { id, text, value, is_selected: false };
                      });
                    break;
                  case COMPONENT_TYPE.FREE_TEXT:
                    formattedOptionsWithRecordResponse = [
                      {
                        id: questionName,
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
    async cleanRecordOrm() {
      await deleteAllRecords();
      await deleteRecordResponsesByUserIdAndResponseId(
        this.userId,
        this.datasetId
      );
      await deleteAllRecordFields();
    },
  },
  beforeDestroy() {
    this.$root.$off("go-to-next-page");
    this.$root.$off("go-to-prev-page");
    this.$root.$off("status-filter-changed");
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: $base-space * 2;
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
</style>
