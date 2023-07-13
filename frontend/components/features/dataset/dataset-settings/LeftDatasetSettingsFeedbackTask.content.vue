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
        :isColorLight="!settingsDescription"
      />
    </div>
    <div class="delete-dataset-component" v-if="dataset">
      <DatasetDeleteFeedbackTaskComponent :dataset="dataset" />
    </div>
  </div>
</template>

<script lang="ts">
export default {
  name: "LeftDatasetSettingsFeedbackTaskContent",
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data() {
    const { fullPath } = this.$route;

    return {
      datasetSettingsUrl: `${window.origin}${fullPath}`,
      datasetName: this.dataset.name,
      datasetTask: this.dataset.task,
      settingsDescription: this.dataset.guidelines,
      settingsDescriptionText:
        this.dataset.guidelines || "This dataset has no annotation guidelines",
    };
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
