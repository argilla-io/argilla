<template>
  <div>
    <BaseLoading v-if="isLoadingDataset" />
    <HeaderAndTopAndOneColumn :key="refreshKey">
      <template v-slot:header>
        <HeaderFeedbackTaskComponent
          :key="datasetId"
          :datasetId="datasetId"
          :breadcrumbs="breadcrumbs"
          :showTrainButton="true"
          :showSettingButton="true"
          :showCopyButton="true"
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
          @refresh="refresh()"
        />
      </template>
      <template v-slot:center>
        <RecordFeedbackTaskAndQuestionnaireContent
          :recordCriteria="recordCriteria"
        />
      </template>
    </HeaderAndTopAndOneColumn>
  </div>
</template>

<script>
import HeaderAndTopAndOneColumn from "@/layouts/HeaderAndTopAndOneColumn";
import { useAnnotationModeViewModel } from "./useAnnotationModeViewModel";

export default {
  name: "DatasetPage",
  components: {
    HeaderAndTopAndOneColumn,
  },
  data() {
    return {
      visibleTrainModal: false,
      refreshKey: 0,
    };
  },
  methods: {
    showTrainModal(value) {
      this.visibleTrainModal = value;
    },
    refresh() {
      this.refreshKey += 1;
    },
  },
  watch: {
    "recordCriteria.committed"() {
      this.updateQueryParams();
    },
  },
  setup() {
    return useAnnotationModeViewModel();
  },
};
</script>
