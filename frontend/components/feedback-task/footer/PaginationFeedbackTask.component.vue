<template>
  <PaginationComponent
    v-if="totalRecord"
    :totalItems="totalRecord"
    @on-paginate="onPaginate"
  />
</template>

<script>
import { getTotalRecordByDatasetId } from "@/models/feedback-task-model/feedback-dataset/feedbackDataset.queries";
export default {
  name: "PaginationFeedbackTaskComponent",
  props: {
    datasetId: {
      type: String,
      required: true,
    },
  },
  computed: {
    totalRecord() {
      return getTotalRecordByDatasetId(this.datasetId);
    },
  },
  methods: {
    onPaginate(currentPage) {
      this.onEmitCurrentPageByBusEvent(currentPage);
    },
    onEmitCurrentPageByBusEvent(currentPage) {
      this.$root.$emit("current-page", currentPage);
    },
  },
  destroyed() {
    this.$root.$off("current-page");
  },
};
</script>

<style lang="scss" scoped></style>
