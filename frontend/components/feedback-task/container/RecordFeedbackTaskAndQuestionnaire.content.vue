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
      sortBy: null,
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
    metadataFilterFromQuery() {
      return this.$route.query?._metadata?.split("+") ?? [];
    },
    sortByFromQuery() {
      return this.$route.query?._sort.split(",") ?? [];
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
      this.metadataToFilterWith,
      this.sortBy
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
        this.metadataToFilterWith,
        this.sortBy
      );
    }

    this.updateTotalRecordsLabel();
    this.fetching = false;
  },
  watch: {
    async currentPage(newValue) {
      await this.routes.addQueryParam({ key: "_page", value: newValue });
    },
    async recordStatusToFilterWith(newValue) {
      await this.routes.addQueryParam(
        { key: "_page", value: this.currentPage },
        { key: "_status", value: newValue }
      );
    },
    async searchTextToFilterWith(newValue) {
      if (newValue)
        return await this.routes.addQueryParam(
          { key: "_page", value: this.currentPage },
          { key: "_search", value: newValue }
        );

      await this.routes.removeQueryParam("_search");
    },
    async metadataToFilterWith(newValue = []) {
      if (newValue.length)
        return await this.routes.addQueryParam(
          { key: "_page", value: this.currentPage },
          { key: "_metadata", value: newValue.join("+") }
        );

      await this.routes.removeQueryParam("_metadata");
    },
    async sortBy(newValue = []) {
      if (newValue.length)
        return await this.routes.addQueryParam(
          { key: "_page", value: this.currentPage },
          { key: "_sort", value: newValue.join(",") }
        );

      await this.routes.removeQueryParam("_sort");
    },
  },
  created() {
    this.recordStatusToFilterWith = this.statusFilterFromQuery;
    this.searchTextToFilterWith = this.searchFilterFromQuery;
    this.metadataToFilterWith = this.metadataFilterFromQuery;
    this.sortBy = this.sortByFromQuery;
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
    this.$root.$on("sort-changed", this.onSortChanged);
  },
  methods: {
    emitResetStatusFilter() {
      this.$root.$emit("reset-status-filter");
    },
    emitResetSearchFilter() {
      this.$root.$emit("reset-search-filter");
    },
    emitResetMetadataFilter() {
      this.$root.$emit("reset-metadata-filter");
    },
    emitResetSort() {
      this.$root.$emit("reset-sort");
    },
    updateTotalRecordsLabel() {
      if (this.searchTextToFilterWith?.length)
        return this.$root.$emit("total-records", this.records.total);

      this.$root.$emit("total-records", null);
    },
    onSearchFilterChanged(newSearchValue) {
      const self = this;
      const onFilter = () => {
        this.searchTextToFilterWith = newSearchValue;
        this.currentPage = 1;

        this.$fetch();
      };

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
            onFilter();
          },
          onClose() {
            self.emitResetSearchFilter();
          },
        });
      }

      if (newSearchValue !== this.searchFilterFromQuery) return onFilter();
    },
    onStatusFilterChanged(newStatus) {
      if (this.recordStatusToFilterWith === newStatus) return;

      const self = this;
      const onFilter = () => {
        this.recordStatusToFilterWith = newStatus;
        this.currentPage = 1;

        this.$fetch();
      };

      if (this.questionFormTouched) {
        Notification.dispatch("notify", {
          message: this.$t("changes_no_submit"),
          buttonText: this.$t("button.ignore_and_continue"),
          numberOfChars: 500,
          type: "warning",
          async onClick() {
            onFilter();
          },
          onClose() {
            self.emitResetStatusFilter();
          },
        });
      } else {
        onFilter();
      }
    },
    onMetadataFilterChanged(metadata) {
      const hasOtherFilter =
        metadata.length !== this.metadataFilterFromQuery.length ||
        metadata.some((e) => !this.metadataFilterFromQuery.includes(e));

      if (!hasOtherFilter) return;

      const self = this;

      const onFilter = () => {
        this.metadataToFilterWith = metadata;
        this.currentPage = 1;

        this.$fetch();
      };

      if (this.questionFormTouched) {
        return Notification.dispatch("notify", {
          message: this.$t("changes_no_submit"),
          buttonText: this.$t("button.ignore_and_continue"),
          numberOfChars: 500,
          type: "warning",
          async onClick() {
            onFilter();
          },
          onClose() {
            self.emitResetMetadataFilter();
          },
        });
      }

      onFilter();
    },
    onSortChanged(sort) {
      const self = this;
      const sortWasChanged =
        sort.length !== this.sortBy.length ||
        sort.some((e) => !this.sortBy.includes(e));

      if (!sortWasChanged) return;

      const onFilter = () => {
        this.sortBy = [...sort, "metadata.loss:desc"];
        this.currentPage = 1;

        this.$fetch();
      };

      if (this.questionFormTouched) {
        return Notification.dispatch("notify", {
          message: this.$t("changes_no_submit"),
          buttonText: this.$t("button.ignore_and_continue"),
          numberOfChars: 500,
          type: "warning",
          async onClick() {
            onFilter();
          },
          onClose() {
            self.emitResetSort();
          },
        });
      }

      onFilter();
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
          this.metadataToFilterWith,
          this.sortBy
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
    this.$root.$off("reset-metadata-filter");
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
