<template>
  <BaseLoading v-if="isLoadingDataset" />
  <HeaderAndTopAndTwoColumns v-else>
    <template v-slot:header>
      <HeaderFeedbackTaskComponent
        :datasetId="datasetId"
        :breadcrumbs="breadcrumbs"
      />
    </template>
    <template v-slot:top>
      <TopDatasetSettingsFeedbackTaskContent :datasetId="datasetId" />
    </template>
    <template v-slot:left>
      <LeftDatasetSettingsFeedbackTaskContent :dataset="dataset" />
    </template>
  </HeaderAndTopAndTwoColumns>
</template>

<script>
import HeaderAndTopAndTwoColumns from "@/layouts/HeaderAndTopAndTwoColumns";
import { useDatasetSettingViewModel } from "./useDatasetSettingViewModel";

export default {
  name: "SettingsPage",
  components: {
    HeaderAndTopAndTwoColumns,
  },
  setup() {
    return useDatasetSettingViewModel();
  },
};
</script>
