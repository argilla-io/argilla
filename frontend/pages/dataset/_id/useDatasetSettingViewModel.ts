import { useRouter } from "@nuxtjs/composition-api";
import { useResolve } from "ts-injecty";
import { Notification } from "@/models/Notifications";
import { GetDatasetByIdUseCase } from "@/v1/domain/usecases/get-dataset-by-id-use.case";
import { TYPE_OF_FEEDBACK } from "@/v1/infrastructure/DatasetRepository";
import { useDataset } from "@/v1/infrastructure/DatasetStorage";

export const useDatasetSettingViewModel = () => {
  const { state: dataset } = useDataset();
  const getDatasetUseCase = useResolve(GetDatasetByIdUseCase);
  const router = useRouter();

  const handleError = (id: string, response: string) => {
    let message = "";
    switch (response) {
      case TYPE_OF_FEEDBACK.ERROR_FETCHING_DATASET_INFO:
        message = `Can't get dataset info for dataset_id: ${id}`;
        break;
      case TYPE_OF_FEEDBACK.ERROR_FETCHING_WORKSPACE_INFO:
        message = `Can't get workspace info for dataset_id: ${id}`;
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

  const loadDataset = async (id: string) => {
    try {
      await getDatasetUseCase.execute(id);
    } catch (error) {
      handleError(id, error.response);

      router.push("/");
    }
  };

  return { loadDataset, dataset };
};
