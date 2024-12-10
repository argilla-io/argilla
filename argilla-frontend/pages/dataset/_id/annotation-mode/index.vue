<template>
  <div>
    <BaseLoading v-if="isLoadingDataset" />
    <AnnotationPage>
      <template v-slot:header>
        <HeaderFeedbackTask
          :key="datasetId"
          :datasetId="datasetId"
          :breadcrumbs="breadcrumbs"
          :showSettingButton="true"
          :showCopyButton="true"
        >
          <template
            slot="topbar-buttons"
            v-if="dataset && dataset.id && user.isAdminOrOwner"
          >
            <ImportData
              v-if="dataset.createdFromUI"
              :snippet="dataset.createCodeSnippetFromHub(user)"
            />
            <ExportToHub :dataset="dataset" />
          </template>
        </HeaderFeedbackTask>
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
