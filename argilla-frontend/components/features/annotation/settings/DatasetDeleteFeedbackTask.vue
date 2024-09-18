<template>
  <div class="dataset-delete">
    <BaseCard
      card-type="danger"
      :title="`<strong>${dataset.name}</strong>`"
      :text="$t('settings.deleteWarning')"
      :buttonText="$t('button.delete')"
      @card-action="toggleDeleteModal(true)"
    />

    <BaseModal
      class="delete-modal"
      :modal-custom="true"
      :prevent-body-scroll="true"
      modal-class="modal-secondary"
      :modal-title="$t('settings.deleteConfirmation')"
      :modal-visible="showDeleteModal"
      @close-modal="toggleDeleteModal(false)"
    >
      <div>
        <p
          v-html="
            $t('settings.deleteConfirmationMessage', {
              datasetName: dataset.name,
              workspaceName: dataset.workspace,
            })
          "
        />
        <div class="modal-buttons">
          <BaseButton class="primary outline" @click="toggleDeleteModal(false)">
            {{ $t("cancel") }}
          </BaseButton>
          <BaseButton class="primary" @click="deleteDataset(dataset)">
            {{ $t("settings.yesDelete") }}
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
