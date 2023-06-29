<template>
  <HeaderAndTopAndTwoColumns v-if="!$fetchState.error && !$fetchState.pending">
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
import { useDatasetSetting } from "./useDatasetSetting";

export default {
  name: "SettingsPage",
  components: {
    HeaderAndTopAndTwoColumns,
  },
  computed: {
    datasetId() {
      return this.$route.params.id;
    },
    breadcrumbs() {
      return [
        { link: { name: "datasets" }, name: "Home" },
        {
          link: { path: `/datasets?workspace=${this.workspace}` },
          name: this.workspace,
        },
        {
          link: {
            name: "dataset-id-annotation-mode",
            params: { id: this.datasetId },
          },
          name: this.datasetName,
        },
        {
          link: null,
          name: "settings",
        },
      ];
    },
  },
  setup() {
    return useDatasetSetting();
  },
  fetch() {
    this.loadDataset(this.datasetId);
  },
};
</script>
