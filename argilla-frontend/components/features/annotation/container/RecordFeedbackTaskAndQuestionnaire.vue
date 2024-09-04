<template>
  <BaseLoading v-if="$fetchState.pending || $fetchState.error" />

  <BulkAnnotation
    v-else-if="
      recordCriteria.committed.page.isBulkMode &&
      recordCriteria.committed.isPending
    "
    :record-criteria="recordCriteria"
    :dataset-vectors="datasetVectors"
    :records="records"
    :record="record"
    :records-message="recordsMessage"
    :status-class="statusClass"
    @on-submit-responses="goToNext"
    @on-discard-responses="goToNext"
  />
  <FocusAnnotation
    v-else
    :record-criteria="recordCriteria"
    :dataset-vectors="datasetVectors"
    :records="records"
    :record="record"
    :records-message="recordsMessage"
    :status-class="statusClass"
    @on-submit-responses="goToNext"
    @on-discard-responses="goToNext"
  />
</template>

<script>
import { useRecordFeedbackTaskViewModel } from "./useRecordFeedbackTaskViewModel";

export default {
  name: "RecordFeedbackTaskAndQuestionnaire",
  props: {
    recordCriteria: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      fetching: false,
    };
  },
  computed: {
    record() {
      return this.records.getRecordOn(this.recordCriteria.committed.page);
    },
    statusClass() {
      return `--${this.record?.status}`;
    },
    shouldShowNotification() {
      return this.record?.isSubmitted && this.record?.isModified;
    },
  },
  async fetch() {
    await this.onLoadRecords();
  },
  methods: {
    async onLoadRecords() {
      if (this.fetching) return Promise.resolve();

      this.fetching = true;

      await this.loadRecords(this.recordCriteria);

      this.fetching = false;
    },
    async paginate() {
      if (this.fetching) return Promise.resolve();

      this.$notification.clear();

      this.fetching = true;

      await this.paginateRecords(this.recordCriteria);

      this.fetching = false;
    },
    onChangeRecordPage(criteria) {
      const filter = async () => {
        await this.paginate();
      };

      this.showNotificationForNewFilterWhenIfNeeded(filter, () =>
        criteria.rollback()
      );
    },
    onChangeRecordFilter(criteria) {
      const filter = async () => {
        await this.onLoadRecords();
      };

      this.showNotificationForNewFilterWhenIfNeeded(filter, () =>
        criteria.rollback()
      );
    },
    goToNext() {
      this.recordCriteria.nextPage();

      this.paginate();
    },
    showNotificationForNewFilterWhenIfNeeded(onFilter, onClose) {
      this.$notification.clear();

      if (!this.shouldShowNotification) {
        return onFilter();
      }

      this.$notification.notify({
        message: this.$t("changes_no_submit"),
        buttonText: this.$t("button.ignore_and_continue"),
        permanent: true,
        type: "warning",
        onClick() {
          return onFilter();
        },
        onClose() {
          return onClose();
        },
      });
    },
  },
  setup(props) {
    return useRecordFeedbackTaskViewModel(props);
  },
  mounted() {
    this.$root.$on("on-change-record-page", this.onChangeRecordPage);

    this.$root.$on(
      "on-change-record-criteria-filter",
      this.onChangeRecordFilter
    );
  },
  destroyed() {
    this.$root.$off("on-change-record-page");
    this.$root.$off("on-change-record-criteria-filter");
    this.$notification.clear();
  },
};
</script>
