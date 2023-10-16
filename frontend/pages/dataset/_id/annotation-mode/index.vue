<template>
  <div>
    <BaseLoading v-if="isLoadingDataset" />
    <HeaderAndTopAndOneColumn>
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
          <DatasetFiltersComponent :recordCriteria="recordCriteria" />
        </section>
      </template>
      <template v-slot:center>
        <RecordFeedbackTaskAndQuestionnaireContent
          :recordCriteria="recordCriteria"
        />
      </template>
      <template v-slot:footer>
        <PaginationFeedbackTaskComponent :recordCriteria="recordCriteria" />
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

<style lang="scss" scoped>
.dataset {
  &__top-area {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
