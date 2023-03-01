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
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from "vuex";
import { getDatasetFromORM } from "@/models/dataset.utilities";
import { getAllLabelsByDatasetId } from "@/models/globalLabel.queries";

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
    };
  },
  computed: {
    dataset() {
      return getDatasetFromORM(this.datasetId, this.datasetTask, false);
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
  },
  methods: {
    ...mapActions({
      onAddNewLabelsInDataset: "entities/datasets/onAddNewLabels",
    }),
    async onAddNewLabels(newLabelsString) {
      const newLabels = this.splitAndTrimArrayString(newLabelsString);
      await this.onAddNewLabelsInDataset({
        datasetId: this.datasetId,
        datasetTask: this.datasetTask,
        newLabels,
      });
    },
    splitAndTrimArrayString(labels) {
      return labels
        .split(this.characterToSeparateLabels)
        .map((item) => item.trim());
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
