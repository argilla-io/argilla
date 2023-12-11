<template>
  <PaginationComponent
    v-if="records.hasRecordsToAnnotate"
    :currentPage="recordCriteria.committed.page"
    :items="records.total"
    @on-click-next="goToNextPage"
    @on-click-prev="goToPrevPage"
  />
</template>

<script>
import { usePaginationFeedbackTaskViewModel } from "./usePaginationFeedbackTaskViewModel";

export default {
  name: "PaginationFeedbackTaskComponent",
  props: {
    recordCriteria: {
      type: Object,
      required: true,
    },
  },
  methods: {
    goToNextPage() {
      this.recordCriteria.nextPage();

      this.$root.$emit("on-change-record-page", this.recordCriteria);
    },
    goToPrevPage() {
      this.recordCriteria.previousPage();

      this.$root.$emit("on-change-record-page", this.recordCriteria);
    },
  },
  setup() {
    return usePaginationFeedbackTaskViewModel();
  },
};
</script>
