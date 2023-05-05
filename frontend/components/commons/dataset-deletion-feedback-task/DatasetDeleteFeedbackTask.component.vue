<template>
  <div class="dataset-delete">
    <h2 class="--heading5 --semibold" v-text="sectionTitle" />
    <BaseCard
      card-type="danger"
      :title="datasetDeleteTitle"
      text="Be careful, this action is not reversible"
      buttonText="Delete dataset"
      @card-action="toggleDeleteModal(true)"
    />

    <BaseModal
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
          <BaseButton class="primary outline" @click="toggleDeleteModal(false)">
            Cancel
          </BaseButton>
          <BaseButton class="primary" @click="onConfirmDeleteDataset">
            Yes, delete
          </BaseButton>
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<script>
import { Notification } from "@/models/Notifications";
import {
  getFeedbackDatasetNameById,
  getFeedbackDatasetWorkspaceNameById,
  deleteDatasetById,
} from "@/models/feedback-task-model/feedback-dataset/feedbackDataset.queries";

const TYPE_OF_FEEDBACK = Object.freeze({
  NOT_ALLOWED_TO_DELETE_DATASET: "NOT_ALLOWED_TO_DELETE_DATASET",
});

export default {
  name: "DatasetDeleteFeedbackTaskComponent",
  props: {
    datasetId: {
      type: String,
      required: true,
    },
  },
  created() {
    this.sectionTitle = "Danger zone";
    this.datasetName = getFeedbackDatasetNameById(this.datasetId);
    this.workspace = getFeedbackDatasetWorkspaceNameById(this.datasetId);

    this.datasetDeleteTitle = `Delete <strong>${this.datasetName}</strong>`;
    this.modalTitle = `Delete confirmation`;
    this.modalDescription = `You are about to delete: <strong>${this.datasetName}</strong> from workspace <strong>${this.workspace}</strong>. This action cannot be undone`;
  },
  data() {
    return {
      showDeleteModal: false,
    };
  },
  methods: {
    toggleDeleteModal(value) {
      this.showDeleteModal = value;
    },
    async onConfirmDeleteDataset() {
      try {
        await this.deleteDataset();
        this.goToDatasetList();
      } catch ({ response }) {
        if (response === TYPE_OF_FEEDBACK.NOT_ALLOWED_TO_DELETE_DATASET) {
          console.log("user is not allowed to delete dataset");
        } else {
          console.log(response);
        }
      } finally {
        this.toggleDeleteModal(false);
      }
    },
    async deleteDataset() {
      let message = "";
      let typeOfNotification = "";
      let statusCall = null;

      const url = this.urlDeleteDatasetV1(this.datasetId);
      try {
        await this.$axios.delete(url);

        // DELETE dataset from the orm
        deleteDatasetById(this.datasetId);

        message = `${this.datasetName} has been deleted`;
        typeOfNotification = "success";
      } catch ({ response }) {
        let { status } = response;
        statusCall = status;
        message = `It is not possible to delete ${this.datasetName}`;
        typeOfNotification = "error";
        if (status === 403) {
          throw { response: TYPE_OF_FEEDBACK.NOT_ALLOWED_TO_DELETE_DATASET };
        }
      } finally {
        statusCall === 403 ||
          Notification.dispatch("notify", {
            message,
            numberOfChars: message?.length,
            type: typeOfNotification,
          });
      }
    },
    urlDeleteDatasetV1(datasetId) {
      return `/v1/datasets/${datasetId}`;
    },
    goToDatasetList() {
      this.$router.push("/");
    },
  },
};
</script>

<style lang="scss" scoped>
.dataset-delete {
  margin-bottom: $base-space * 5;
}
</style>
