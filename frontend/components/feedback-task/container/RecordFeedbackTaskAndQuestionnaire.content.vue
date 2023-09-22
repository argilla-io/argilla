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
import { RECORD_STATUS } from "@/models/feedback-task-model/record/record.queries";
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
      metadataToFilterWith: null,
      currentPage: null,
      fetching: false,
    };
  },
  computed: {
    noMoreDataMessage() {
      return `You've reached the end of the data for the ${this.recordStatusToFilterWith} queue.`;
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
      return `--${this.record.status}`;
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
      this.recordStatusToFilterWith,
      this.searchTextToFilterWith,
      this.metadataToFilterWith
    );

    const isRecordExistForCurrentPage = this.records.existsRecordOn(
      this.currentPage
    );

    if (!isRecordExistForCurrentPage && this.currentPage !== 1) {
      this.currentPage = 1;

      await this.loadRecords(
        this.datasetId,
        this.currentPage,
        this.recordStatusToFilterWith,
        this.searchTextToFilterWith,
        this.metadataToFilterWith
      );
    }

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
    this.$root.$on("metadata-filter-changed", this.onMetadataFilterChanged);
  },
  methods: {
    async applyStatusFilter(status) {
      this.recordStatusToFilterWith = status;
      this.currentPage = 1;

      await this.$fetch();

      this.checkAndEmitTotalRecords();
    },
    async applySearchFilter(searchFilter) {
      this.searchTextToFilterWith = searchFilter;
      this.currentPage = 1;

      await this.$fetch();

      this.checkAndEmitTotalRecords();
    },
    async applyMetadataFilter(metadata) {
      this.metadataToFilterWith = metadata;
      this.currentPage = 1;

      await this.$fetch();

      this.checkAndEmitTotalRecords();
    },
    emitResetStatusFilter() {
      this.$root.$emit("reset-status-filter");
    },
    emitResetSearchFilter() {
      this.$root.$emit("reset-search-filter");
    },
    checkAndEmitTotalRecords() {
      if (this.searchTextToFilterWith?.length)
        return this.$root.$emit("total-records", this.records.total);

      this.$root.$emit("total-records", null);
    },
    async onSearchFilterChanged(newSearchValue) {
      const localApplySearchFilter = this.applySearchFilter;
      const localEmitResetSearchFilter = this.emitResetSearchFilter;

      if (
        this.questionFormTouched &&
        newSearchValue !== this.searchFilterFromQuery
      ) {
        return Notification.dispatch("notify", {
          message: this.$t("changes_no_submit"),
          buttonText: this.$t("button.ignore_and_continue"),
          numberOfChars: 500,
          type: "warning",
          async onClick() {
            await localApplySearchFilter(newSearchValue);
          },
          onClose() {
            localEmitResetSearchFilter();
          },
        });
      }

      if (newSearchValue !== this.searchFilterFromQuery)
        return await this.applySearchFilter(newSearchValue);
    },
    async onStatusFilterChanged(newStatus) {
      if (this.recordStatusToFilterWith === newStatus) {
        return;
      }

      const localApplyStatusFilter = this.applyStatusFilter;
      const localEmitResetStatusFilter = this.emitResetStatusFilter;

      if (this.questionFormTouched) {
        Notification.dispatch("notify", {
          message: this.$t("changes_no_submit"),
          buttonText: this.$t("button.ignore_and_continue"),
          numberOfChars: 500,
          type: "warning",
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
    async onMetadataFilterChanged(metadata) {
      const self = this;

      if (this.questionFormTouched) {
        return Notification.dispatch("notify", {
          message: this.$t("changes_no_submit"),
          buttonText: this.$t("button.ignore_and_continue"),
          numberOfChars: 500,
          type: "warning",
          async onClick() {
            await self.applyMetadataFilter(metadata);
          },
          onClose() {
            //TODO:
          },
        });
      }

      await this.applyMetadataFilter(metadata);
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
          this.recordStatusToFilterWith,
          this.searchTextToFilterWith,
          this.metadataToFilterWith
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
    this.$root.$off("metadata-filter-changed");
    Notification.dispatch("clear");
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
</style>
