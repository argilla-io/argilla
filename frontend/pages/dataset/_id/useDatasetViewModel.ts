import { computed, ref, useRoute, useRouter } from "@nuxtjs/composition-api";
import { useResolve } from "ts-injecty";
import { Notification } from "@/models/Notifications";
import { GetDatasetByIdUseCase } from "@/v1/domain/usecases/get-dataset-by-id-use-case";
import { DATASET_API_ERRORS } from "@/v1/infrastructure/repositories/DatasetRepository";
import { useDataset } from "@/v1/infrastructure/storage/DatasetStorage";
import { Dataset } from "@/v1/domain/entities/Dataset";

export const useDatasetViewModel = () => {
  const isLoadingDataset = ref(false);
  const router = useRouter();
  const route = useRoute();
  const datasetId = route.value.params.id;

  const { state: dataset } = useDataset();
  const getDatasetUseCase = useResolve(GetDatasetByIdUseCase);

  const breadcrumbs = computed(() => createBreadcrumbs(dataset));

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

    const paramsForNotification = {
      message,
      numberOfChars: message.length,
      type: "error",
    };

    Notification.dispatch("notify", paramsForNotification);
  };

  const createBreadcrumbs = (dataset: Dataset) => {
    return [
      { link: { name: "datasets" }, name: "Home" },
      {
        link: { path: `/datasets?workspaces=${dataset.workspace}` },
        name: dataset.workspace,
      },
      {
        link: {
          name: null,
        },
        name: dataset.name,
      },
    ];
  };

  const loadDataset = async () => {
    try {
      isLoadingDataset.value = true;

      await getDatasetUseCase.execute(datasetId);
    } catch (error) {
      handleError(error.response);

      router.push("/");
    } finally {
      isLoadingDataset.value = false;
    }
  };

  return { dataset, datasetId, isLoadingDataset, loadDataset, breadcrumbs };
};
