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
          :datasetName="dataset.name"
          :workspaceName="dataset.workspace"
        />
      </BaseModal>
    </template>
    <template v-slot:sidebar-right>
      <SidebarFeedbackTaskComponent
        :datasetId="datasetId"
        @refresh="loadDataset()"
      />
    </template>
    <template v-slot:top>
      <section class="dataset__top-area">
        <DatasetFiltersComponent :datasetId="datasetId" />
      </section>
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
import { useAnnotationModeViewModel } from "./useAnnotationModeViewModel";

export default {
  name: "DatasetPage",
  components: {
    HeaderAndTopAndOneColumn,
  },
  data() {
    return {
      visibleTrainModal: false,
    };
  },
  created() {
    this.checkIfUrlHaveRecordStatusOrInitiateQueryParams();
  },
  methods: {
    checkIfUrlHaveRecordStatusOrInitiateQueryParams() {
      this.$route.query?._status ??
        this.$router.replace({
          query: {
            ...this.$route.query,
            _page: 1,
            _status: RECORD_STATUS.PENDING.toLowerCase(),
          },
        });
    },
    showTrainModal(value) {
      this.visibleTrainModal = value;
    },
  },
  setup() {
    return useAnnotationModeViewModel();
  },
};
</script>

<style lang="scss" scoped>
.dataset {
  &__top-area {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
