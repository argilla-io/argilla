import { ref, useRoute } from "@nuxtjs/composition-api";
import { DATASET_API_ERRORS } from "@/v1/infrastructure/repositories/DatasetRepository";
import { Dataset } from "~/v1/domain/entities/dataset/Dataset";
import { useTranslate } from "~/v1/infrastructure/services";
import { useNotifications } from "~/v1/infrastructure/services/useNotifications";

export const useDatasetViewModel = () => {
  const isLoadingDataset = ref(false);
  const route = useRoute();
  const notification = useNotifications();
  const { t } = useTranslate();
  const datasetId = route.value.params.id;

  const handleError = (response: string) => {
    let message = "";
    switch (response) {
      case DATASET_API_ERRORS.ERROR_FETCHING_DATASET_INFO:
        message = `Can't get dataset info for dataset_id: ${datasetId}`;
        break;
      case DATASET_API_ERRORS.ERROR_FETCHING_WORKSPACE_INFO:
        message = `Can't get workspace info for dataset_id: ${datasetId}`;
        break;
      default:
        message =
          "There was an error on fetching dataset info and workspace info. Please try again";
    }

    notification.notify({
      message,
      type: "danger",
    });
  };

  const createRootBreadCrumbs = (dataset: Dataset) => {
    return [
      { link: { name: "datasets" }, name: t("breadcrumbs.home") },
      {
        link: { path: `/datasets?workspaces=${dataset.workspace}` },
        name: dataset.workspace,
      },
      {
        link: { path: "annotation-mode" },
        name: dataset.name,
      },
    ];
  };

  return {
    datasetId,
    isLoadingDataset,
    handleError,
    createRootBreadCrumbs,
  };
};
