<template>
  <HeaderAndTopAndTwoColumns v-if="!$fetchState.error && !$fetchState.pending">
    <template v-slot:header>
      <!-- <HeaderComponent /> -->
    </template>
    <template v-slot:top>
      <TopDatasetSettingsFeedbackTaskContent :datasetId="datasetId" />
    </template>
    <template v-slot:left>
      <!-- <LeftDatasetSettingsContent /> -->
    </template>
    <template v-slot:right>
      <div class="right-content"></div>
    </template>
  </HeaderAndTopAndTwoColumns>
</template>

<script>
import HeaderAndTopAndTwoColumns from "@/layouts/HeaderAndTopAndTwoColumns";
import {
  upsertFeedbackDataset,
  isDatasetByIdExists,
} from "@/models/feedback-task-model/feedback-dataset/feedbackDataset.queries";

const TYPE_OF_FEEDBACK = Object.freeze({
  ERROR_FETCHING_DATASET_INFO: "ERROR_FETCHING_DATASET_INFO",
  ERROR_FETCHING_WORKSPACE_INFO: "ERROR_FETCHING_WORKSPACE_INFO",
});
export default {
  name: "SettingsPage",
  components: {
    HeaderAndTopAndTwoColumns,
  },
  computed: {
    datasetId() {
      return this.$route.params.id;
    },
  },
  async fetch() {
    try {
      const isDatasetStoredInOrm = isDatasetByIdExists(this.datasetId);
      if (!isDatasetStoredInOrm) {
        // 1- fetch dataset info
        const dataset = await this.getDatasetInfo(this.datasetId);

        // 2- fetch workspace info
        const workspace = await this.getWorkspaceInfo(dataset.workspace_id);

        // 3- insert in ORM
        upsertFeedbackDataset({ ...dataset, workspace_name: workspace });
      }
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
