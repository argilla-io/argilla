import { useResolve } from "ts-injecty";
import { ref } from "vue-demi";
import { Notification } from "~/models/Notifications";
import { Dataset } from "~/v1/domain/entities/Dataset";
import { DeleteDatasetUseCase } from "~/v1/domain/usecases/delete-dataset-use-case";
import { useRoutes } from "~/v1/infrastructure/services";

export const useDeleteDatasetViewModel = () => {
  const showDeleteModal = ref(false);
  const deleteDatasetUseCase = useResolve(DeleteDatasetUseCase);
  const routes = useRoutes();

  const toggleDeleteModal = (show: boolean) => {
    showDeleteModal.value = show;
  };

  const deleteDataset = async (dataset: Dataset) => {
    try {
      await deleteDatasetUseCase.execute(dataset.id);

      Notification.dispatch("notify", {
        message: `${dataset.name} has been deleted`,
        type: "success",
      });

      routes.goToDatasetsList();
    } catch {
      toggleDeleteModal(false);

      Notification.dispatch("notify", {
        message: `It is not possible to delete ${dataset.name}`,
        type: "error",
      });
    }
  };

  return { toggleDeleteModal, showDeleteModal, deleteDataset };
};
