<template>
  <div v-if="!$fetchState.pending && !$fetchState.error" class="wrapper">
    <template v-if="!!record">
      <RecordFeedbackTaskComponent
        :recordStatus="record.status"
        :fields="record.fields"
      />
      <QuestionsFormComponent
        :key="record.id"
        class="question-form"
        :class="statusClass"
        :datasetId="datasetId"
        :record="record"
        @on-submit-responses="goToNext"
        @on-discard-responses="goToNext"
        @on-question-form-touched="onQuestionFormTouched"
      />
    </template>

    <div v-else class="wrapper--empty">
      <p
        v-if="!records.hasRecordsToAnnotate"
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
  RECORD_STATUS,
  RESPONSE_STATUS_FOR_API,
} from "@/models/feedback-task-model/record/record.queries";
import { LABEL_PROPERTIES } from "../../feedback-task/feedbackTask.properties";
import { useRecordFeedbackTaskViewModel } from "./useRecordFeedbackTaskViewModel";

export default {
  name: "RecordFeedbackTaskAndQuestionnaireComponent",
  props: {
    datasetId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      questionFormTouched: false,
      recordStatusToFilterWith: null,
      searchTextToFilterWith: null,
      currentPage: null,
      totalRecords: null,
      numberOfFetch: 0,
      fetching: false,
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
      return this.records.getRecordOn(this.currentPage);
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
      return `--${this.record.status.toLowerCase()}`;
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
    if (this.fetching) return Promise.resolve();

    this.fetching = true;
    this.clearRecords();

    await this.loadRecords(
      this.datasetId,
      this.currentPage,
      this.recordStatusFilterValueForGetRecords,
      this.searchTextToFilterWith
    );

    const isRecordExistForCurrentPage = this.records.existsRecordOn(
      this.currentPage
    );

    if (!isRecordExistForCurrentPage && this.currentPage !== 1) {
      this.currentPage = 1;

      await this.loadRecords(
        this.datasetId,
        this.currentPage,
        this.recordStatusFilterValueForGetRecords,
        this.searchTextToFilterWith
      );
    }

    this.numberOfFetch++;
    this.fetching = false;
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
  },
  created() {
    this.recordStatusToFilterWith = this.statusFilterFromQuery;
    this.searchTextToFilterWith = this.searchFilterFromQuery;
    this.currentPage = this.pageFromQuery;

    this.loadMetrics(this.datasetId);
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
    async applyStatusFilter(status) {
      this.currentPage = 1;
      this.recordStatusToFilterWith = status;

      await this.$fetch();

      this.checkAndEmitTotalRecords({
        searchFilter: this.searchTextToFilterWith,
        value: this.records.total,
      });
    },
    async applySearchFilter(searchFilter) {
      this.currentPage = 1;
      this.searchTextToFilterWith = searchFilter;

      await this.$fetch();

      this.checkAndEmitTotalRecords({
        searchFilter,
        value: this.records.total,
      });
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
      if (this.fetching) return Promise.resolve();

      this.fetching = true;

      let isNextRecordExist = this.records.existsRecordOn(newPage);

      if (!isNextRecordExist) {
        await this.loadRecords(
          this.datasetId,
          newPage,
          this.recordStatusFilterValueForGetRecords,
          this.searchTextToFilterWith
        );

        isNextRecordExist = this.records.existsRecordOn(newPage);
      }

      if (isNextRecordExist) {
        this.currentPage = newPage;
      } else if (this.currentPage < newPage) {
        Notification.dispatch("notify", {
          message: this.noMoreDataMessage,
          numberOfChars: this.noMoreDataMessage.length,
          type: "info",
        });
      }

      this.fetching = false;
    },
    goToNext() {
      this.setCurrentPage(this.currentPage + 1);
    },
  },
  beforeDestroy() {
    this.$root.$off("go-to-next-page");
    this.$root.$off("go-to-prev-page");
    this.$root.$off("status-filter-changed");
    this.$root.$off("search-filter-changed");
  },
  setup() {
    return useRecordFeedbackTaskViewModel();
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
