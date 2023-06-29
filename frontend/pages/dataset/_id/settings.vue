<template>
  <HeaderAndTopAndTwoColumns v-if="!$fetchState.error && !$fetchState.pending">
    <template v-slot:header>
      <HeaderFeedbackTaskComponent
        v-if="datasetName && workspace"
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
    <template v-slot:right>
      <div class="right-content"></div>
    </template>
  </HeaderAndTopAndTwoColumns>
</template>

<script>
import HeaderAndTopAndTwoColumns from "@/layouts/HeaderAndTopAndTwoColumns";
import {
  getFeedbackDatasetNameById,
  getFeedbackDatasetWorkspaceNameById,
} from "@/models/feedback-task-model/feedback-dataset/feedbackDataset.queries";
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
    datasetName() {
      return getFeedbackDatasetNameById(this.datasetId);
    },
    workspace() {
      return getFeedbackDatasetWorkspaceNameById(this.datasetId);
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
    this.loadDataset(this.datasetId, this.$axios);
  },
};
</script>
