import {
  onBeforeMount,
  ref,
  useRoute,
  useRouter,
} from "@nuxtjs/composition-api";
import { useResolve } from "ts-injecty";
import { Notification } from "@/models/Notifications";
import { GetDatasetByIdUseCase } from "~/v1/domain/usecases/get-dataset-by-id-use-case";
import { DATASET_API_ERRORS } from "~/v1/infrastructure/repositories/DatasetRepository";
import { useDataset } from "@/v1/infrastructure/storage/DatasetStorage";

export const useDatasetSettingViewModel = () => {
  const isLoadingDataset = ref(false);
  const router = useRouter();
  const route = useRoute();
  const datasetId = route.value.params.id;

  const { state: dataset } = useDataset();
  const getDatasetUseCase = useResolve(GetDatasetByIdUseCase);

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

  onBeforeMount(() => {
    loadDataset();
  });

  return { dataset, datasetId, isLoadingDataset, loadDataset };
};
