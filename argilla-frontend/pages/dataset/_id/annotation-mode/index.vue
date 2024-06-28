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
        />
      </template>
      <template v-slot:center>
        <div class="center">
          <PersistentStorageBanner />
          <RecordFeedbackTaskAndQuestionnaire
            :recordCriteria="recordCriteria"
          />
        </div>
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

<style scoped>
.center {
  height: 100%;
  max-height: 100%;
  display: flex;
  flex-direction: column;
}
</style>
