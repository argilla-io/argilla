<template>
  <BaseLoading v-if="isLoadingDataset" />
  <HeaderAndTopAndOneColumn v-else>
    <template v-slot:header>
      <HeaderFeedbackTaskComponent
        :key="datasetId"
        :datasetId="datasetId"
        :breadcrumbs="breadcrumbs"
        :showTrainButton="true"
        @on-click-train="showTrainModal(true)"
      />
      <BaseModal
        :modal-custom="true"
        :prevent-body-scroll="true"
        modal-class="modal-auto"
        modal-position="modal-top-center"
        :modal-visible="visibleTrainModal"
        allow-close
        @close-modal="showTrainModal(false)"
      >
        <DatasetTrainComponent
          datasetTask="FeedbackTask"
          :datasetName="datasetName"
          :workspaceName="workspace"
        />
      </BaseModal>
    </template>
    <template v-slot:sidebar-right>
      <SidebarFeedbackTaskComponent
        :datasetId="datasetId"
        @refresh="onRefresh()"
      />
    </template>
    <template v-slot:top>
      <DatasetFiltersComponent :datasetId="datasetId" />
    </template>
    <template v-slot:center>
      <RecordFeedbackTaskAndQuestionnaireContent :datasetId="datasetId" />
    </template>
    <template v-slot:footer>
      <PaginationFeedbackTaskComponent :datasetId="datasetId" />
    </template>
  </HeaderAndTopAndOneColumn>
</template>

<script>
import HeaderAndTopAndOneColumn from "@/layouts/HeaderAndTopAndOneColumn";
import { RECORD_STATUS } from "@/models/feedback-task-model/record/record.queries";
import { LABEL_PROPERTIES } from "@/components/feedback-task/feedbackTask.properties";
import { Notification } from "@/models/Notifications";

import { useAnnotationModeViewModel } from "./useAnnotationModeViewModel";

export default {
  name: "DatasetPage",
  components: {
    HeaderAndTopAndOneColumn,
  },
  data() {
    return {
      areResponsesUntouched: true,
      visibleTrainModal: false,
    };
  },
  beforeRouteLeave(to, from, next) {
    const isNotificationForThisRoute =
      !this.areResponsesUntouched &&
      ["datasets", "dataset-id-settings", "user-settings"].includes(to.name);

    if (isNotificationForThisRoute) {
      this.showNotification({
        eventToFireOnClick: next,
        message: this.toastMessageOnLeavingRoute,
        buttonMessage: this.buttonMessage,
      });
    } else {
      next();
    }
  },
  computed: {
    datasetName() {
      return this.dataset.name;
    },
    workspace() {
      return this.dataset.workspace;
    },
  },
  created() {
    this.onBusEventAreResponsesUntouched();
    this.checkIfUrlHaveRecordStatusOrInitiateQueryParams();

    this.toastMessageOnRefresh =
      "Your changes will be lost if you refresh the page";
    this.toastMessageOnLeavingRoute =
      "Your changes will be lost if you leave the current page";
    this.buttonMessage = LABEL_PROPERTIES.CONTINUE;
  },
  methods: {
    checkIfUrlHaveRecordStatusOrInitiateQueryParams() {
      this.$route.query?._status ??
        this.$router.replace({
          query: {
            ...this.$route.query,
            _search: "",
            _page: 1,
            _status: RECORD_STATUS.PENDING.toLowerCase(),
          },
        });
    },
    onRefresh() {
      if (this.areResponsesUntouched) {
        return this.loadDataset();
      }

      this.showNotification({
        eventToFireOnClick: async () => {
          this.loadDataset();
        },
        message: this.toastMessageOnRefresh,
        buttonMessage: this.buttonMessage,
      });
    },
    onBusEventAreResponsesUntouched() {
      this.$root.$on("are-responses-untouched", (areResponsesUntouched) => {
        this.areResponsesUntouched = areResponsesUntouched;
      });
    },
    showNotification({ eventToFireOnClick, message, buttonMessage }) {
      Notification.dispatch("notify", {
        message: message ?? "",
        numberOfChars: 500,
        type: "warning",
        buttonText: buttonMessage ?? "",
        async onClick() {
          eventToFireOnClick();
        },
      });
    },
    showTrainModal(value) {
      this.visibleTrainModal = value;
    },
  },
  destroyed() {
    this.$root.$off("are-responses-untouched");
    Notification.dispatch("clear");
  },
  setup() {
    return useAnnotationModeViewModel();
  },
};
</script>
