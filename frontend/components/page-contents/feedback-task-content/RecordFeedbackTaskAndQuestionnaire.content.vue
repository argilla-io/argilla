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
        @on-submit-responses="goToNextPageAndRefreshMetrics"
        @on-discard-responses="goToNextPageAndRefreshMetrics"
        @on-clear-responses="refreshMetrics"
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
import { upsertDatasetMetrics } from "@/models/feedback-task-model/dataset-metric/datasetMetric.queries.js";
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
  data() {
    return {
      reRenderQuestionForm: 1,
      questionFormTouched: false,
      recordStatusToFilterWith: null,
      searchTextToFilterWith: null,
      currentPage: null,
      totalRecords: null,
      numberOfFetch: 0,
    };
  },
  computed: {
    filterParams() {
      return {
        _search: this.searchTextToFilterWith,
        _page: this.currentPage,
        _status: this.recordStatusToFilterWith,
      };
    },
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
      // TODO - do this in a hook instead of computed => it's expensive
      return this.questions?.map((question) => {
        const correspondingResponseToQuestion =
          this.recordResponsesFromCurrentUser.find(
            (recordResponse) => question.name === recordResponse.question_name
          );

        if (correspondingResponseToQuestion) {
          let formattedOptions = [];

          // TODO - remove is_selected from object pass to the free_text case and ensure we can submit a form with one text
          switch (question.component_type) {
            case COMPONENT_TYPE.RANKING:
              formattedOptions = correspondingResponseToQuestion.options;
              break;
            case COMPONENT_TYPE.FREE_TEXT:
            case COMPONENT_TYPE.SINGLE_LABEL:
            case COMPONENT_TYPE.MULTI_LABEL:
            case COMPONENT_TYPE.RATING:
              formattedOptions = correspondingResponseToQuestion.options.map(
                (option) => {
                  return {
                    ...option,
                    is_selected: option.is_selected || false,
                  };
                }
              );
              break;
            default:
              console.log(
                `The component ${question.component_type} is unknown`
              );
          }
          return {
            ...question,
            response_id: correspondingResponseToQuestion.id,
            options: formattedOptions,
          };
        }
        if (
          question.component_type === COMPONENT_TYPE.RATING ||
          question.component_type === COMPONENT_TYPE.SINGLE_LABEL ||
          question.component_type === COMPONENT_TYPE.MULTI_LABEL
        ) {
          const formattedOptions = question.options.map((option) => {
            return { ...option, is_selected: false };
          });
          return { ...question, options: formattedOptions, response_id: null };
        }

        if (question.component_type === COMPONENT_TYPE.RANKING) {
          const formattedOptions = question.options.map((option) => {
            return { ...option, rank: null };
          });
          return { ...question, options: formattedOptions, response_id: null };
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
      if (
        isNil(this.searchTextToFilterWith) ||
        this.searchTextToFilterWith.length === 0
      )
        return `You have no ${this.recordStatusToFilterWith} records`;
      return `You have no ${this.recordStatusToFilterWith} records matching the search input`;
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
    searchFilterFromQuery() {
      return this.$route.query?._search ?? "";
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

    this.numberOfFetch++;
  },
  watch: {
    async currentPage(newValue) {
      // TODO - regroup in a common watcher hover filterParams computed
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
      // TODO - regroup in a common watcher hover filterParams computed
      await this.$router.push({
        path: this.$route.path,
        query: {
          ...this.$route.query,
          _status: newValue,
          _search: this.searchTextToFilterWith,
          _page: this.currentPage,
        },
      });
    },
    async searchTextToFilterWith(newValue) {
      // TODO - regroup in a common watcher hover filterParams computed
      await this.$router.push({
        path: this.$route.path,
        query: {
          ...this.$route.query,
          _search: newValue,
          _status: this.recordStatusToFilterWith,
          _page: this.currentPage,
        },
      });
    },
    numberOfFetch(newValue) {
      const isFetchCalledForTheFirstTime = newValue === 1;

      if (isFetchCalledForTheFirstTime) {
        this.checkAndEmitTotalRecords({
          searchFilter: this.searchTextToFilterWith,
          value: this.totalRecords,
        });
      }
    },
  },
  async created() {
    this.recordStatusToFilterWith = this.statusFilterFromQuery;
    this.searchTextToFilterWith = this.searchFilterFromQuery;
    this.currentPage = this.pageFromQuery;

    await this.refreshMetrics();
  },
  mounted() {
    this.$root.$on("go-to-next-page", () => {
      this.setCurrentPage(this.currentPage + 1);
    });
    this.$root.$on("go-to-prev-page", () => {
      this.setCurrentPage(this.currentPage - 1);
    });
    this.$root.$on("status-filter-changed", this.onStatusFilterChanged);
    this.$root.$on("search-filter-changed", this.onSearchFilterChanged);
  },
  methods: {
    async refreshMetrics() {
      const datasetMetrics = await this.fetchMetrics();

      const formattedMetrics = this.factoryDatasetMetricsForOrm(datasetMetrics);

      await upsertDatasetMetrics(formattedMetrics);
    },
    async fetchMetrics() {
      try {
        const { data } = await this.$axios.get(
          `/v1/me/datasets/${this.datasetId}/metrics`
        );

        return data;
      } catch (err) {
        console.log(err);
      }
    },
    factoryDatasetMetricsForOrm({ records, responses, user_id }) {
      const {
        count: responsesCount,
        submitted: responsesSubmitted,
        discarded: responsesDiscarded,
      } = responses;

      return {
        dataset_id: this.datasetId,
        user_id: user_id ?? this.userId,
        total_record: records?.count ?? 0,
        responses_count: responsesCount,
        responses_submitted: responsesSubmitted,
        responses_discarded: responsesDiscarded,
      };
    },
    async applyStatusFilter(status) {
      this.recordStatusToFilterWith = status;
      this.currentPage = 1;

      await this.$fetch();

      this.checkAndEmitTotalRecords({
        searchFilter: this.searchTextToFilterWith,
        value: this.totalRecords,
      });

      this.reRenderQuestionForm++;
    },
    async applySearchFilter(searchFilter) {
      // NOTE - the order of both next line is important because of the watcher update
      this.currentPage = 1;
      this.searchTextToFilterWith = searchFilter;

      await this.$fetch();

      this.checkAndEmitTotalRecords({ searchFilter, value: this.totalRecords });

      this.reRenderQuestionForm++;
    },
    emitResetStatusFilter() {
      this.$root.$emit("reset-status-filter");
    },
    emitResetSearchFilter() {
      this.$root.$emit("reset-search-filter");
    },
    checkAndEmitTotalRecords({ searchFilter, value }) {
      // NOTE - update the totalRecords to show ONLY if a search input is applied
      if (searchFilter?.length) {
        this.$root.$emit("total-records", value);
      } else {
        this.$root.$emit("total-records", null);
      }
    },
    async onSearchFilterChanged(newSearchValue) {
      const localApplySearchFilter = this.applySearchFilter;
      const localEmitResetSearchFilter = this.emitResetSearchFilter;

      if (
        this.questionFormTouched &&
        newSearchValue !== this.searchFilterFromQuery
      ) {
        Notification.dispatch("notify", {
          message: "Your changes will be lost if you apply the search filter",
          numberOfChars: 500,
          type: "warning",
          buttonText: LABEL_PROPERTIES.CONTINUE,
          async onClick() {
            await localApplySearchFilter(newSearchValue);
          },
          onClose() {
            localEmitResetSearchFilter();
          },
        });
      } else {
        await this.applySearchFilter(newSearchValue);
      }
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
    async goToNextPageAndRefreshMetrics() {
      this.setCurrentPage(this.currentPage + 1);
      await this.refreshMetrics();
    },
    async initRecordsInDatabase(
      offset,
      status = this.recordStatusFilterValueForGetRecords,
      searchText = this.searchTextToFilterWith
    ) {
      let records = [];
      let totalRecords = null;

      if (isNil(searchText) || !searchText.length) {
        // FETCH records from offset, status + 10 next records
        ({ items: records } = await this.getRecords(
          this.datasetId,
          offset,
          status
        ));
      } else {
        ({ items: records, totalRecords } = await this.searchRecords(
          this.datasetId,
          offset,
          status,
          searchText
        ));
      }

      this.totalRecords = isNil(totalRecords) ? null : totalRecords;

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
    async searchRecords(
      datasetId,
      offset,
      responseStatus,
      searchText,
      numberOfRecordsToFetch = 10
    ) {
      try {
        const url = `/v1/me/datasets/${datasetId}/records/search`;

        const body = JSON.parse(
          JSON.stringify({
            query: {
              text: {
                q: searchText,
              },
            },
          })
        );

        const params = {
          include: "responses",
          response_status: responseStatus,
          limit: numberOfRecordsToFetch,
          offset,
        };

        const { data } = await this.$axios.post(url, body, { params });
        const { items, total: totalRecords } = data;

        const formattedItems = items.map((item) => item.record);
        return { items: formattedItems, totalRecords };
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
                  case COMPONENT_TYPE.MULTI_LABEL:
                    optionsByQuestionName.forEach(({ id, text, value }) => {
                      const isValueInRecordResponse =
                        recordResponseByQuestionName.value.includes(value);

                      formattedOptionsWithRecordResponse.push({
                        id,
                        text,
                        value,
                        is_selected: isValueInRecordResponse,
                      });
                    });
                    break;
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
                  case COMPONENT_TYPE.RANKING:
                    formattedOptionsWithRecordResponse =
                      optionsByQuestionName.map(({ id, text, value }) => {
                        const correspondingResponse =
                          recordResponseByQuestionName.value.find(
                            (response) => response.value === value
                          );

                        if (correspondingResponse) {
                          return {
                            id,
                            text,
                            value,
                            rank: correspondingResponse.rank ?? null,
                          };
                        }
                        return { id, text, value, rank: null };
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
    this.$root.$off("search-filter-changed");
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
  background: palette(white);
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
