<template>
  <div class="left-content">
    <div class="left-content-item dataset-description">
      <div class="item">
        <p class="dataset-name" v-text="datasetName" />
        <p class="dataset-task" v-if="datasetTask" v-html="datasetTask" />
      </div>
      <base-action-tooltip tooltip="Copied">
        <base-button
          title="Copy to clipboard"
          class="secondary small"
          @click.prevent="$copyToClipboard(datasetSettingsUrl)"
        >
          Copy link
        </base-button>
      </base-action-tooltip>
    </div>
    <div class="dataset-description-component left-content-item">
      <DatasetDescriptionComponent
        :datasetDescription="settingsDescriptionText"
        :lightColor="!settingsDescription"
      />
    </div>
    <div class="delete-dataset-component" v-if="datasetId">
      <DatasetDeleteFeedbackTaskComponent :datasetId="datasetId" />
    </div>
  </div>
</template>

<script>
import {
  getFeedbackDatasetNameById,
  getDatasetTaskByDatasetId,
  getDatasetGuidelinesByDatasetId,
} from "@/models/feedback-task-model/feedback-dataset/feedbackDataset.queries";
export default {
  name: "LeftDatasetSettingsFeedbackTaskContent",
  props: {
    datasetId: {
      type: String,
      required: true,
    },
  },
  beforeMount() {
    const { fullPath } = this.$route;

    this.datasetSettingsUrl = `${window.origin}${fullPath}`;
    this.datasetName = getFeedbackDatasetNameById(this.datasetId);
    this.datasetTask = getDatasetTaskByDatasetId(this.datasetId);
    this.settingsDescription = getDatasetGuidelinesByDatasetId(this.datasetId);
    this.settingsDescriptionText =
      this.settingsDescription || "This dataset has no annotation guidelines";
  },
};
</script>

<style lang="scss" scoped>
.left-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
  .dataset-description {
    display: flex;
    align-items: center;
    min-height: 5em;
    .item {
      flex: 1;
      display: flex;
      align-items: center;
      gap: $base-space * 2;
    }
  }
}

.left-content-item {
  border-bottom: 1px solid $black-10;
}

.labels-edition-component {
  min-height: 15em;
  padding-bottom: $base-space * 4;
  &__content {
    max-width: calc(100% - 150px);
  }
}
.dataset-name {
  @include font-size(16px);
}
.dataset-task {
  color: $black-54;
  border: 1px solid $black-37;
  border-radius: $border-radius-m;
  padding: calc($base-space / 2);
  @include font-size(12px);
  @include line-height(12px);
}
</style>
