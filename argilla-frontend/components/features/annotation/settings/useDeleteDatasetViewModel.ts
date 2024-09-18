import { useResolve } from "ts-injecty";
import { ref } from "vue-demi";
import { Dataset } from "~/v1/domain/entities/dataset/Dataset";
import { DeleteDatasetUseCase } from "~/v1/domain/usecases/delete-dataset-use-case";
import { useRoutes } from "~/v1/infrastructure/services";
import { useNotifications } from "~/v1/infrastructure/services/useNotifications";

export const useDeleteDatasetViewModel = () => {
  const showDeleteModal = ref(false);
  const notification = useNotifications();
  const deleteDatasetUseCase = useResolve(DeleteDatasetUseCase);
  const routes = useRoutes();

  const toggleDeleteModal = (show: boolean) => {
    showDeleteModal.value = show;
  };

  const deleteDataset = async (dataset: Dataset) => {
    try {
      await deleteDatasetUseCase.execute(dataset.id);

      notification.notify({
        message: `${dataset.name} has been deleted`,
        type: "success",
      });

      routes.goToDatasetsList();
    } catch {
      toggleDeleteModal(false);

      notification.notify({
        message: `It is not possible to delete ${dataset.name}`,
        type: "danger",
      });
    }
  };

  return { toggleDeleteModal, showDeleteModal, deleteDataset };
};
