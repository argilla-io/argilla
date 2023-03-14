<template>
  <div class="wrapper">
    <div class="header">
      <h2 class="--heading5 --semibold description__title" v-html="title" />
    </div>
    <div class="content">
      <BaseSpinner v-if="isLoading" />

      <BaseFeedbackComponent
        v-if="!numberOfLabels && !isLoading"
        :feedbackInput="inputForEmptyLabelsFeedback"
        class="feedback-area"
      />

      <BaseFeedbackComponent
        v-if="feedbackInputIfThereIsLabelsNotSavedInBack && !isLoading"
        :feedbackInput="feedbackInputIfThereIsLabelsNotSavedInBack"
        @on-click="onSaveLabelsNotPersisted"
        class="feedback-area"
      />

      <TokenClassificationGlobalLabelsComponent
        v-if="isTaskTokenClassification && numberOfLabels && !isLoading"
        :labels="labels"
        :showAllLabels="showAllLabels"
        @on-toggle-show-less-more-labels="showAllLabels = !showAllLabels"
      />

      <TextClassificationGlobalLabelsComponent
        v-if="isTaskTextClassification && numberOfLabels && !isLoading"
        :labels="labels"
        :showAllLabels="showAllLabels"
        @on-toggle-show-less-more-labels="showAllLabels = !showAllLabels"
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
    isLoading: {
      type: Boolean,
      default: () => true,
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
      inputForEmptyLabelsFeedback: {
        message:
          "You still have no labels in your dataset, start by creating some",
        feedbackType: "ERROR",
      },
      showAllLabels: false,
    };
  },
  computed: {
    dataset() {
      return getDatasetFromORM(this.datasetId, this.datasetTask, false);
    },
    datasetName() {
      return this.dataset?.name;
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
    numberOfLabels() {
      return this.labels.length;
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
      try {
        await this.onAddNewLabelsInDataset({
          datasetId: this.datasetId,
          datasetTask: this.datasetTask,
          newLabels,
        });
        this.toggleShowAllLabels(true);
      } catch (err) {
        console.log(err);
      }
    },
    async onSaveLabelsNotPersisted() {
      const newLabels = this.labelsTextNotSavedInBack;
      try {
        await this.onAddNewLabelsInDataset({
          datasetId: this.datasetId,
          datasetTask: this.datasetTask,
          newLabels,
        });
        this.toggleShowAllLabels(true);
      } catch (err) {
        console.log(err);
      }
    },
    splitTrimArrayString(labels, splitCharacter = null) {
      return labels.split(splitCharacter).map((item) => item.trim());
    },
    toggleShowAllLabels(trueOrFalse) {
      this.showAllLabels = trueOrFalse;
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
  margin-bottom: $base-space * 5;
}

.buttons-area {
  display: inline-flex;
  align-items: baseline;
}
</style>
