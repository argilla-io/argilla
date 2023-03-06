<template>
  <div class="wrapper">
    <div class="header">
      <h2 class="--heading5 --semibold description__title" v-html="title" />
    </div>
    <div class="content">
      <div class="feedback-area">
        <BaseFeedbackComponent
          v-if="feedbackInputIfThereIsLabelsNotSavedInBack"
          :feedbackInput="feedbackInputIfThereIsLabelsNotSavedInBack"
          @on-click="onSaveLabelsNotPersisted"
        />
      </div>

      <BaseSpinner v-if="isloading" />

      <TokenClassificationGlobalLabelsComponent
        v-if="isTaskTokenClassification && !isloading"
        :labels="labels"
      />
      <TextClassificationGlobalLabelsComponent
        v-if="isTaskTextClassification && !isloading"
        :labels="labels"
      />
      <div class="buttons-area">
        <CreateNewAction
          text="+ Create label"
          v-if="allowAddNewLabel"
          @new-label="onAddNewLabels"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from "vuex";
import { getDatasetFromORM } from "@/models/dataset.utilities";
import {
  getAllLabelsByDatasetId,
  getLabelsNotSavedInBackByDatasetId,
  isExistAnyLabelsNotSavedInBackByDatasetId,
} from "@/models/globalLabel.queries";
import { getLoadingValue } from "@/models/viewSettings.queries";

export default {
  name: "EditionLabelComponent",
  props: {
    title: {
      type: String,
      default: () => "Labels",
    },
    datasetId: {
      type: Array,
      required: true,
    },
    datasetTask: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      isSortAsc: true,
      sortBy: "order",
      allowAddNewLabel: true,
      characterToSeparateLabels: null,
      saveLabelsButtonLabel: "Save labels",
      inputForFeedbackComponent: {
        message:
          "Action needed: Add or save labels to validate the annotation schema",
        buttonLabels: [{ label: "Save schema", value: "SAVE_SCHEMA" }],
        feedbackType: "ERROR",
      },
    };
  },
  computed: {
    dataset() {
      return getDatasetFromORM(this.datasetId, this.datasetTask, false);
    },
    datasetName() {
      return this.dataset?.name;
    },
    isloading() {
      return getLoadingValue(this.datasetName)?.loading ?? false;
    },
    isTaskTokenClassification() {
      return this.datasetTask === "TokenClassification";
    },
    isTaskTextClassification() {
      return this.datasetTask === "TextClassification";
    },
    labels() {
      return getAllLabelsByDatasetId(
        this.datasetId,
        this.sortBy,
        this.isSortAsc
      );
    },
    labelsInGlobalLabelsNotSavedInBack() {
      return getLabelsNotSavedInBackByDatasetId(this.datasetId);
    },
    labelsTextNotSavedInBack() {
      return this.labelsInGlobalLabelsNotSavedInBack.reduce(
        (acc, curr) => acc.concat(curr.text),
        []
      );
    },
    isAnyLabelsInGlobalLabelsModelNotSavedInBack() {
      return isExistAnyLabelsNotSavedInBackByDatasetId(this.datasetId);
    },
    feedbackInputIfThereIsLabelsNotSavedInBack() {
      if (this.isAnyLabelsInGlobalLabelsModelNotSavedInBack) {
        return this.inputForFeedbackComponent;
      }
      return null;
    },
  },
  methods: {
    ...mapActions({
      onAddNewLabelsInDataset: "entities/datasets/onAddNewLabels",
    }),
    async onAddNewLabels(newLabelsString) {
      const newLabels = this.splitTrimArrayString(
        newLabelsString,
        this.characterToSeparateLabels
      );
      await this.onAddNewLabelsInDataset({
        datasetId: this.datasetId,
        datasetTask: this.datasetTask,
        newLabels,
      });
    },
    async onSaveLabelsNotPersisted() {
      const newLabels = this.labelsTextNotSavedInBack;
      await this.onAddNewLabelsInDataset({
        datasetId: this.datasetId,
        datasetTask: this.datasetTask,
        newLabels,
      });
    },
    splitTrimArrayString(labels, splitCharacter = null) {
      return labels.split(splitCharacter).map((item) => item.trim());
    },
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-direction: column;
  .header {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
  }
  .content {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }
}

.feedback-area {
  display: inline-flex;
}

.buttons-area {
  display: inline-flex;
  align-items: baseline;
}
</style>
