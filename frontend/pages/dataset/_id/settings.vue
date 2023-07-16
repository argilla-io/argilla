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
  computed: {
    breadcrumbs() {
      return [
        { link: { name: "datasets" }, name: "Home" },
        {
          link: { path: `/datasets?workspace=${this.dataset.workspace}` },
          name: this.dataset.workspace,
        },
        {
          link: {
            name: "dataset-id-annotation-mode",
            params: { id: this.datasetId },
          },
          name: this.dataset.name,
        },
        {
          link: null,
          name: "settings",
        },
      ];
    },
  },
  setup() {
    return useDatasetSettingViewModel();
  },
};
</script>
