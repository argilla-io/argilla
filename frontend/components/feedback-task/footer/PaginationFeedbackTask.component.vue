<template>
  <PaginationComponent
    v-if="totalRecord"
    :totalItems="10"
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
      console.log(currentPage);
    },
  },
};
</script>

<style lang="scss" scoped></style>
