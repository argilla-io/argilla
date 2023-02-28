<template>
  <div class="dataset-settings-page">
    <div
      class="labels-edition"
      v-if="isTaskTokenClassification || isTaskTextClassification"
    >
      <EditionLabelComponent
        :datasetId="datasetId"
        :datasetTask="datasetTask"
      />
    </div>
  </div>
</template>

<script>
import { mapActions } from "vuex";
import {
  ObservationDataset,
  getDatasetModelPrimaryKey,
} from "@/models/Dataset";

export default {
  name: "SettingsPage",
  computed: {
    datasetName() {
      return this.$route.params.dataset;
    },
    datasetWorkspace() {
      return this.$route.params.workspace;
    },
    datasetId() {
      return getDatasetModelPrimaryKey({
        name: this.datasetName,
        workspace: this.datasetWorkspace,
      });
    },
    dataset() {
      return ObservationDataset.query().whereId(this.datasetId).first();
    },
    datasetTask() {
      return this.dataset?.task;
    },
    isTaskTokenClassification() {
      return this.datasetTask === "TokenClassification";
    },
    isTaskTextClassification() {
      return this.datasetTask === "TextClassification";
    },
  },
  async fetch() {
    //  Fetch the record data and initialize the corresponding data models and fetch labels
    await this.fetchByName(this.datasetName);
  },
  methods: {
    ...mapActions({
      fetchByName: "entities/datasets/fetchByName",
    }),
  },
};
</script>

<style lang="scss" scoped>
.dataset-settings-page {
}
</style>
