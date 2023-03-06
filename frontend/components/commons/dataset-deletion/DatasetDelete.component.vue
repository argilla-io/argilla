<template>
  <div class="dataset-delete" v-if="datasetName">
    <h2 class="--heading5 --semibold">{{ sectionTitle }}</h2>
    <base-card
      card-type="danger"
      :title="datasetDeleteTitle"
      text="Be careful, this action is not reversible"
      buttonText="Delete dataset"
      @card-action="toggleDeleteModal(true)"
    />
    <base-modal
      class="delete-modal"
      :modal-custom="true"
      :prevent-body-scroll="true"
      modal-class="modal-secondary"
      :modal-title="modalTitle"
      :modal-visible="showDeleteModal"
      @close-modal="toggleDeleteModal(false)"
    >
      <div>
        <p v-html="modalDescription"></p>
        <div class="modal-buttons">
          <base-button
            class="primary outline"
            @click="toggleDeleteModal(false)"
          >
            Cancel
          </base-button>
          <base-button class="primary" @click="onConfirmDeleteDataset">
            Yes, delete
          </base-button>
        </div>
      </div>
    </base-modal>
  </div>
</template>

<script>
import { mapActions } from "vuex";
import { currentWorkspace } from "@/models/Workspace";
import { getDatasetFromORM } from "@/models/dataset.utilities";
export default {
  props: {
    datasetId: {
      type: Array,
      required: true,
    },
    datasetTask: {
      type: String,
      required: true,
    },
  },
  data: () => {
    return {
      sectionTitle: "Danger zone",
      showDeleteModal: false,
    };
  },
  computed: {
    dataset() {
      return getDatasetFromORM(this.datasetId, this.datasetTask);
    },
    datasetName() {
      return this.dataset?.name;
    },
    datasetDeleteTitle() {
      return `Delete ${this.datasetName}`;
    },
    modalTitle() {
      return `Delete confirmation`;
    },
    modalDescription() {
      return `You are about to delete: <strong>${this.datasetName}</strong> from workspace <strong>${this.workspace}</strong>. This action cannot be undone`;
    },
    workspace() {
      return currentWorkspace(this.$route);
    },
  },
  methods: {
    ...mapActions({
      deleteDataset: "entities/datasets/deleteDataset",
    }),
    async onConfirmDeleteDataset() {
      try {
        await this.deleteSelectedDataset();
        this.goToDatasetList();
      } catch (error) {
        console.log(error);
      } finally {
        this.toggleDeleteModal(false);
      }
    },
    toggleDeleteModal(value) {
      this.showDeleteModal = value;
    },
    goToDatasetList() {
      this.$router.push("/");
    },
    async deleteSelectedDataset() {
      await this.deleteDataset({
        workspace: this.workspace,
        name: this.datasetName,
      });
    },
  },
};
</script>
<style lang="scss" scoped>
.dataset-delete {
  margin-bottom: $base-space * 5;
}
</style>
