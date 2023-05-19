<template>
  <PaginationComponent
    v-if="totalRecord"
    :key="totalRecord"
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
import { LABEL_PROPERTIES } from "@/components/feedback-task/feedbackTask.properties";
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
      message: "Your changes will be lost if you move to another page",
      buttonMessage: LABEL_PROPERTIES.CONTINUE,
      typeOfToast: "warning",
    };

    this.onBusEventAreResponsesUntouched();
  },
  data() {
    return {
      areResponsesUntouched: true,
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
    onBusEventAreResponsesUntouched() {
      this.$root.$on("are-responses-untouched", (areResponsesUntouched) => {
        this.areResponsesUntouched = areResponsesUntouched;
      });
    },
    onEmitCurrentPageByBusEvent(currentPage) {
      this.$root.$emit("current-page", currentPage);
    },
    conditionToShowNotificationComponent() {
      // NOTE 1 - this method have to be passed to the generic pagination component to keep it 'stupid'
      // NOTE 2 - return true if responses have been touched,return false in other case

      return !this.areResponsesUntouched;
    },
  },
  destroyed() {
    this.$root.$off("are-responses-untouched");
  },
};
</script>
