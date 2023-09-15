<template>
  <PaginationComponent
    v-if="hasRecords"
    :currentPage="currentPage"
    @on-click-next="onPaginate(goToNextPage)"
    @on-click-prev="onPaginate(goToPrevPage)"
  />
</template>

<script>
import { isNil } from "lodash";
import { Notification } from "@/models/Notifications";
import { usePaginationFeedbackTaskViewModel } from "./usePaginationFeedbackTaskViewModel";

export default {
  name: "PaginationFeedbackTaskComponent",
  props: {
    datasetId: {
      type: String,
      required: true,
    },
  },
  created() {
    this.onBusEventGoToNextPage();
  },
  computed: {
    currentPage() {
      const { _page } = this.$route.query;
      switch (_page) {
        case isNil(_page):
        case _page < 1:
          return 1;
        default:
          return +_page;
      }
    },
    hasRecords() {
      return this.records.hasRecordsToAnnotate;
    },
  },
  methods: {
    goToNextPage() {
      this.$root.$emit("go-to-next-page");
    },
    goToPrevPage() {
      this.$root.$emit("go-to-prev-page");
    },
    onBusEventGoToNextPage() {
      this.$root.$on("go-to-page", (newPage) => {
        this.currentPage = newPage;
      });
    },
    showNotificationBeforePaginate(eventToFire) {
      // TODO - move logic to show notification in RecordFeedbackAndQuestionnaire component
      Notification.dispatch("notify", {
        message: this.$t("changes_no_submit"),
        buttonText: this.$t("button.ignore_and_continue"),
        numberOfChars: 500,
        type: "warning",
        async onClick() {
          eventToFire();
        },
      });
    },
    onPaginate(eventToFire) {
      if (this.isQuestionsFormTouched) {
        this.showNotificationBeforePaginate(eventToFire);
      } else {
        eventToFire();
      }
    },
  },
  destroyed() {
    this.$root.$off("go-to-page");
    Notification.dispatch("clear");
  },
  setup() {
    return usePaginationFeedbackTaskViewModel();
  },
};
</script>
