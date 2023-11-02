<template>
  <BaseLoading v-if="$fetchState.pending || $fetchState.error" />
  <div v-else class="wrapper">
    <template v-if="!!record">
      <RecordFieldsAndSimilarity
        :key="`${record.id}_fields`"
        class="wrapper__fields"
        :datasetVectors="datasetVectors"
        :records="records"
        :recordCriteria="recordCriteria"
        :record="record"
      />

      <QuestionsFormComponent
        :key="`${record.id}_questions`"
        class="wrapper__form"
        :class="statusClass"
        :datasetId="recordCriteria.datasetId"
        :record="record"
        @on-submit-responses="goToNext"
        @on-discard-responses="goToNext"
      />
    </template>

    <div v-if="!records.hasRecordsToAnnotate" class="wrapper--empty">
      <p class="wrapper__text --heading3" v-text="noRecordsMessage" />
    </div>
  </div>
</template>

<script>
import { Notification } from "@/models/Notifications";
import { useRecordFeedbackTaskViewModel } from "./useRecordFeedbackTaskViewModel";

export default {
  name: "RecordFeedbackTaskAndQuestionnaireComponent",
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
    noMoreDataMessage() {
      return `You've reached the end of the data for the ${this.recordCriteria.committed.status} queue.`;
    },
    noRecordsMessage() {
      const { status } = this.recordCriteria.committed;

      if (this.recordCriteria.isFilteredByText)
        return `You have no ${status} records matching the search input`;

      return `You have no ${status} records`;
    },
    statusClass() {
      return `--${this.record.status}`;
    },
    shouldShowNotification() {
      return this.record?.isSubmitted && this.record?.isModified;
    },
  },
  async fetch() {
    await this.onLoadRecords("replace");
  },
  methods: {
    async onLoadRecords(mode) {
      if (this.fetching) return Promise.resolve();

      this.fetching = true;

      await this.loadRecords(mode, this.recordCriteria);

      this.onSearchFinished();

      this.fetching = false;
    },
    async paginate() {
      if (this.fetching) return Promise.resolve();

      Notification.dispatch("clear");

      this.fetching = true;

      const isNextRecordExist = await this.paginateRecords(this.recordCriteria);

      if (!isNextRecordExist) {
        setTimeout(() => {
          Notification.dispatch("notify", {
            message: this.noMoreDataMessage,
            numberOfChars: this.noMoreDataMessage.length,
            type: "info",
          });
        }, 100);
      }

      this.onSearchFinished();
      this.fetching = false;
    },
    onChangeRecordPage(criteria) {
      const filter = async () => {
        await this.paginate();
      };

      this.showNotificationForNewFilterWhenIfNeeded(filter, () =>
        criteria.reset()
      );
    },
    onChangeRecordFilter(criteria) {
      const filter = async () => {
        await this.onLoadRecords("replace");
      };

      this.showNotificationForNewFilterWhenIfNeeded(filter, () =>
        criteria.reset()
      );
    },
    onSearchFinished() {
      return this.$root.$emit("on-changed-total-records", this.records.total);
    },
    goToNext() {
      this.recordCriteria.nextPage();

      this.paginate();
    },
    showNotificationForNewFilterWhenIfNeeded(onFilter, onClose) {
      Notification.dispatch("clear");

      if (!this.shouldShowNotification) {
        return onFilter();
      }

      setTimeout(() => {
        Notification.dispatch("notify", {
          message: this.$t("changes_no_submit"),
          buttonText: this.$t("button.ignore_and_continue"),
          numberOfChars: 500,
          type: "warning",
          onClick() {
            Notification.dispatch("clear");
            return onFilter();
          },
          onClose() {
            Notification.dispatch("clear");
            return onClose();
          },
        });
      }, 100);
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
    Notification.dispatch("clear");
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: $base-space * 2;
  height: 100%;
  padding: 0 $base-space * 3 $base-space * 2 $base-space * 3;
  @include media("<tablet") {
    flex-flow: column;
    overflow: auto;
  }
  &__fields,
  &__form {
    @include media("<tablet") {
      overflow: visible;
      height: auto;
      max-height: none;
    }
  }
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
