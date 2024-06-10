<template>
  <div>
    <BaseLoading v-if="isLoadingDataset" />
    <AnnotationPage>
      <template v-slot:header>
        <HeaderFeedbackTask
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
          <DatasetTrain
            :datasetName="dataset.name"
            :workspaceName="dataset.workspace"
          />
        </BaseModal>
      </template>
      <template v-slot:center>
        <PersistentStorageBanner />
        <RecordFeedbackTaskAndQuestionnaire :recordCriteria="recordCriteria" />
      </template>
    </AnnotationPage>
  </div>
</template>

<script>
import AnnotationPage from "@/layouts/AnnotationPage";
import { useAnnotationModeViewModel } from "./useAnnotationModeViewModel";

export default {
  name: "DatasetPage",
  components: {
    AnnotationPage,
  },
  data() {
    return {
      visibleTrainModal: false,
    };
  },
  methods: {
    showTrainModal(value) {
      this.visibleTrainModal = value;
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
