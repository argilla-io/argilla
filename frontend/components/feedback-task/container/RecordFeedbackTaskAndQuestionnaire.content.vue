<template>
  <BaseLoading v-if="$fetchState.pending || $fetchState.error" />
  <div v-else class="wrapper">
    <template v-if="!!record">
      <RecordFeedbackTaskComponent
        :key="`${record.id}_${record.status}_fields`"
        :recordStatus="record.status"
        :fields="record.fields"
      />

      <QuestionsFormComponent
        :key="`${record.id}_${record.status}_questions`"
        class="question-form"
        :class="statusClass"
        :datasetId="recordCriteria.datasetId"
        :record="record"
        @on-submit-responses="goToNext"
        @on-discard-responses="goToNext"
        @on-question-form-touched="onQuestionFormTouched"
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
      questionFormTouched: false,
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

      if (this.recordCriteria.isFilteringByText)
        return `You have no ${status} records matching the search input`;

      return `You have no ${status} records`;
    },
    statusClass() {
      return `--${this.record.status}`;
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
        Notification.dispatch("notify", {
          message: this.noMoreDataMessage,
          numberOfChars: this.noMoreDataMessage.length,
          type: "info",
        });
      }

      this.onSearchFinished();
      this.fetching = false;
    },
    onSearchFinished() {
      return this.$root.$emit("on-changed-total-records", this.records.total);
    },
    onQuestionFormTouched(isTouched) {
      this.questionFormTouched = isTouched;
    },
    goToNext() {
      this.recordCriteria.nextPage();

      this.paginate();
    },
    showNotificationForNewFilter(onFilter, onClose) {
      Notification.dispatch("clear");

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
  setup() {
    return useRecordFeedbackTaskViewModel();
  },
  created() {
    this.$root.$on("on-change-record-page", async (criteria) => {
      const filter = async () => {
        await this.paginate();
        this.record?.initialize();
      };

      if (this.questionFormTouched) {
        return this.showNotificationForNewFilter(filter, () =>
          criteria.reset()
        );
      }

      await filter();
    });

    this.$root.$on("on-change-record-criteria-filter", async (criteria) => {
      const filter = async () => {
        await this.onLoadRecords("replace");
        this.record?.initialize();
      };

      if (this.questionFormTouched) {
        return this.showNotificationForNewFilter(filter, () =>
          criteria.reset()
        );
      }

      await filter();
    });
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
