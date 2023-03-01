<template>
  <HeaderAndTopAndTwoColumns>
    <template v-slot:top>
      <div class="dataset-info">DatasetSettgingsinfo</div>
    </template>
    <template v-slot:left>
      <div class="left-content">
        <div class="dataset-description-component">
          <DatasetDescriptionComponent
            :datasetDescription="settingsDescription"
          />
        </div>
        <div
          class="labels-edition-component"
          v-if="isTaskTokenClassification || isTaskTextClassification"
        >
          <EditionLabelComponent
            :datasetId="datasetId"
            :datasetTask="datasetTask"
          />
        </div>
        <div class="delete-dataset-component" v-if="datasetTask">
          <DatasetDeleteComponent
            :datasetId="datasetId"
            :datasetTask="datasetTask"
          />
        </div>
      </div>
    </template>
    <template v-slot:right>
      <div class="right-content"></div>
    </template>
  </HeaderAndTopAndTwoColumns>
</template>

<script>
import { mapActions } from "vuex";
import HeaderAndTopAndTwoColumns from "@/layouts/HeaderAndTopAndTwoColumns";
import {
  ObservationDataset,
  getDatasetModelPrimaryKey,
} from "@/models/Dataset";

export default {
  name: "SettingsPage",
  components: { HeaderAndTopAndTwoColumns },
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
    settingsDescription() {
      return "Soon you will be able to edit your information";
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
.left-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
</style>
