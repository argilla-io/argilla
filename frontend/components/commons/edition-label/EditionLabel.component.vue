<template>
  <div class="wrapper">
    <div class="header">
      <h2 class="--heading5 --semibold description__title" v-html="title" />
    </div>
    <div class="content">
      <TokenClassificationGlobalLabelsComponent
        v-if="isTaskTokenClassification"
        :labels="labels"
      />
      <TextClassificationGlobalLabelsComponent
        v-if="isTaskTextClassification"
        :labels="labels"
      />
      <div class="buttons-area">
        <create-new-action
          v-if="allowAddNewLabel"
          @new-label="onAddNewLabels"
        />
        <BaseButton
          @click.prevent="onSaveLabelsNotPersisted"
          v-if="isAnyLabelsInGlobalLabelsModelNotSavedInBack"
        >
          {{ saveLabelsButtonLabel }}
        </BaseButton>
      </div>
      <p v-html="messageFeedbackIfThereIsLabelsNotSavedInBack" />
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
      saveLabelsButtonLabel: "Saved labels",
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
    messageFeedbackIfThereIsLabelsNotSavedInBack() {
      if (this.isAnyLabelsInGlobalLabelsModelNotSavedInBack) {
        return `The label schema from the dataset ${this.datasetName} is empty. Click on <em>
        ${this.saveLabelsButtonLabel}</em> to save all labels from aggregations`;
      }
      return null;
    },
  },
  methods: {
    ...mapActions({
      onAddNewLabelsInDataset: "entities/datasets/onAddNewLabels",
    }),
    async onAddNewLabels(newLabelsString) {
      const newLabels = this.splitAndTrimArrayString(
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
    splitAndTrimArrayString(labels, splitCharacter = null) {
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
.buttons-area {
  display: inline-flex;
}
</style>
