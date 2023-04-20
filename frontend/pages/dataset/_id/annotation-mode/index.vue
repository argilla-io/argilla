<template>
  <HeaderAndTopAndOneColumn v-if="!$fetchState.pending && !$fetchState.error">
    <template v-slot:header>
      <HeaderFeedbackTaskComponent
        v-if="datasetName && workspace"
        :datasetName="datasetName"
        :workspace="workspace"
        :breadcrumbs="breadcrumbs"
      />
    </template>
    <template v-slot:sidebar-right>
      <SidebarFeedbackTaskComponent />
    </template>
    <template v-slot:center>
      <CenterFeedbackTaskContent :datasetId="datasetId" />
    </template>
    <template v-slot:footer>
      <PaginationFeedbackTaskComponent :datasetId="datasetId" />
    </template>
  </HeaderAndTopAndOneColumn>
</template>

<script>
import HeaderAndTopAndOneColumn from "@/layouts/HeaderAndTopAndOneColumn";
import {
  upsertFeedbackDataset,
  getFeedbackDatasetNameById,
  getFeedbackDatasetWorkspaceNameById,
} from "@/models/feedback-task-model/feedback-dataset/feedbackDataset.queries";
import { Notification } from "@/models/Notifications";

const TYPE_OF_FEEDBACK = Object.freeze({
  ERROR_FETCHING_DATASET_INFO: "ERROR_FETCHING_DATASET_INFO",
  ERROR_FETCHING_WORKSPACE_INFO: "ERROR_FETCHING_WORKSPACE_INFO",
});

export default {
  name: "DatasetPage",
  components: {
    HeaderAndTopAndOneColumn,
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
            name: null,
            params: { workspace: this.workspace, dataset: this.datasetName },
          },
          name: this.datasetName,
        },
      ];
    },
  },
  async fetch() {
    try {
      // 1- fetch dataset info
      const dataset = await this.getDatasetInfo(this.datasetId);

      // TODO - remove step 2 when workspace name will be include in the getDatasetInfo API call
      // 2- fetch workspace info
      const workspace = await this.getWorkspaceInfo(dataset.workspace_id);

      // 3- insert in ORM
      upsertFeedbackDataset({ ...dataset, workspace_name: workspace });
    } catch (err) {
      this.manageErrorIfFetchNotWorking(err);
    }
  },
  methods: {
    async getDatasetInfo(datasetId) {
      try {
        const { data } = await this.$axios.get(`/v1/datasets/${datasetId}`);

        return data;
      } catch (err) {
        throw {
          response: TYPE_OF_FEEDBACK.ERROR_FETCHING_DATASET_INFO,
        };
      }
    },
    async getWorkspaceInfo(workspaceId) {
      try {
        const { data: responseWorkspace } = await this.$axios.get(
          `/v1/workspaces/${workspaceId}`
        );

        const { name } = responseWorkspace || { name: null };

        return name;
      } catch (err) {
        throw {
          response: TYPE_OF_FEEDBACK.ERROR_FETCHING_WORKSPACE_INFO,
        };
      }
    },
    manageErrorIfFetchNotWorking({ response }) {
      this.initErrorNotification(response);
      this.$router.push("/");
    },
    initErrorNotification(response) {
      let message = "";
      switch (response) {
        case TYPE_OF_FEEDBACK.ERROR_FETCHING_DATASET_INFO:
          message = `Can't get dataset info for dataset_id: ${this.datasetId}`;
          break;
        case TYPE_OF_FEEDBACK.ERROR_FETCHING_WORKSPACE_INFO:
          message = `Can't get workspace info for dataset_id: ${this.datasetId}`;
          break;
        default:
          message = `There was an error on fetching dataset info and workspace info. Please try again`;
      }

      const paramsForNotitification = {
        message,
        numberOfChars: message.length,
        type: "error",
      };

      Notification.dispatch("notify", paramsForNotitification);
    },
  },
};
</script>
