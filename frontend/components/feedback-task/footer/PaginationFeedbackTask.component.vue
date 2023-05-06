<template>
  <PaginationComponent
    v-if="totalRecord"
    :showPageNumber="false"
    :totalItems="totalRecord"
    :notificationParams="paginationNotificationParams"
    :conditionToShowNotificationComponentOnPagination="
      conditionToShowNotificationComponent
    "
    @on-paginate="onPaginate"
  />
</template>

<script>
import { getTotalRecordByDatasetId } from "@/models/feedback-task-model/feedback-dataset/feedbackDataset.queries";
import { getRecordStatusByDatasetIdAndRecordIndex } from "@/models/feedback-task-model/record/record.queries";
import { RECORD_STATUS } from "@/models/feedback-task-model/record/record.queries";

export default {
  name: "PaginationFeedbackTaskComponent",
  props: {
    datasetId: {
      type: String,
      required: true,
    },
  },
  created() {
    this.paginationNotificationParams = {
      message: "Pending actions will be lost when the page is refreshed",
      buttonMessage: "Ok, got it!",
      typeOfToast: "warning",
    };
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
    conditionToShowNotificationComponent(currentPage) {
      // NOTE 1 - this method have to be passed to the generic pagination component to keep it 'stupid'
      // NOTE 2 - this function is only validate if one record is showned
      // NOTE 3 - record_index start at 0 and page at 1.
      const recordIndex = currentPage - 1;
      const recordStatusOfTheCurrentRecord =
        getRecordStatusByDatasetIdAndRecordIndex(this.datasetId, recordIndex);

      let showNotification = false;
      switch (recordStatusOfTheCurrentRecord) {
        case RECORD_STATUS.PENDING:
          showNotification = true;
          break;
        case RECORD_STATUS.SUBMITTED:
        case RECORD_STATUS.DISCARDED:
          showNotification = false;
          break;
        default:
          console.log(
            `The status ${recordStatusOfTheCurrentRecord} is unknown`
          );
      }

      return showNotification;
    },
  },
  destroyed() {
    this.$root.$off("current-page");
  },
};
</script>

<style lang="scss" scoped></style>
