<template>
  <div v-if="helpContents.length">
    <base-button
      title="Info"
      class="help-info__action-button"
      :class="buttonClass"
      @click="showHelpModal()"
    >
      <svgicon name="support" width="18" height="18" />Help</base-button
    >
    <lazy-base-modal
      modal-class="modal-secondary"
      modal-position="modal-top-right"
      :modal-custom="true"
      :modal-visible="isModalVisible"
      @close-modal="close()"
    >
      <help-info-content :help-contents="helpContents" />
      <div class="help-info__buttons">
        <base-button class="primary" @click="close()">Ok, got it!</base-button>
      </div>
    </lazy-base-modal>
  </div>
</template>

<script>
import "assets/icons/support";
import { getDatasetFromORM } from "@/models/dataset.utilities";
import { getViewSettingsByDatasetName } from "@/models/viewSettings.queries";
export default {
  props: {
    datasetId: {
      type: Array,
      required: true,
    },
    datasetName: {
      type: String,
      required: true,
    },
    datasetTask: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      isModalVisible: false,
      similarity: {
        id: "similarity",
        name: "Similarity Search",
        component: "helpInfoSimilarity",
      },
      explain: {
        id: "explain",
        name: "Colors in token attributions",
        component: "helpInfoExplain",
      },
    };
  },
  computed: {
    dataset() {
      return getDatasetFromORM(this.datasetId, this.datasetTask);
    },
    helpContents() {
      return [
        ...this.setHelpContent(this.similarity, this.availableSimilarity),
        ...this.setHelpContent(this.explain, this.availableExplain),
      ];
    },
    availableSimilarity() {
      return this.viewSettings.viewMode !== "labelling-rules";
    },
    availableExplain() {
      //TODO: to replace when record will have a corresponding table
      return this.dataset?.results.records.some((record) => record.explanation);
    },
    viewSettings() {
      return getViewSettingsByDatasetName(this.datasetName);
    },
    buttonClass() {
      return this.isModalVisible ? "--active" : null;
    },
  },
  methods: {
    setHelpContent(obj, condition) {
      return condition ? [obj] : [];
    },
    showHelpModal() {
      this.isModalVisible = !this.isModalVisible;
    },
    close() {
      this.isModalVisible = false;
    },
  },
};
</script>

<style lang="scss" scoped>
.help-info {
  &__action-button {
    padding: 0;
    color: $primary-color;
    &:hover,
    &.--active {
      color: darken($primary-color, 15%);
    }
  }
  &__buttons {
    display: flex;
    justify-content: right;
  }
}
</style>
