<template>
  <div class="dataset-delete">
    <BaseCard
      card-type="danger"
      :title="`<strong>${dataset.name}</strong>`"
      text="Be careful, this action is not reversible"
      buttonText="Delete"
      @card-action="toggleDeleteModal(true)"
    />

    <BaseModal
      class="delete-modal"
      :modal-custom="true"
      :prevent-body-scroll="true"
      modal-class="modal-secondary"
      :modal-title="'Delete confirmation'"
      :modal-visible="showDeleteModal"
      @close-modal="toggleDeleteModal(false)"
    >
      <div>
        <p>
          You are about to delete:
          <strong> {{ this.dataset.name }}</strong> from workspace
          <strong> {{ dataset.workspace }}</strong
          >. This action cannot be undone
        </p>
        <div class="modal-buttons">
          <BaseButton class="primary outline" @click="toggleDeleteModal(false)">
            Cancel
          </BaseButton>
          <BaseButton class="primary" @click="deleteDataset(dataset)">
            Yes, delete
          </BaseButton>
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<script>
import { useDeleteDatasetViewModel } from "./useDeleteDatasetViewModel";

export default {
  name: "DatasetDeleteFeedbackTask",
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  setup() {
    return useDeleteDatasetViewModel();
  },
};
</script>

<style lang="scss" scoped>
.dataset-delete {
  margin-bottom: $base-space * 5;
}
</style>
